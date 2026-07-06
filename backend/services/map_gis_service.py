"""
Map GIS Service — provides geospatial operations for Smart City GIS Dashboard.
"""

import math
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Complaint, Resource, ComplaintCategory, Severity, ComplaintStatus, ResourceType, ResourceStatus
from services.map_service import MapService, WARD_COORDS, BASE_LAT, BASE_LNG
from repositories.weather_repository import WeatherRepository

logger = logging.getLogger("citypilot.map_gis")


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Computes the convex hull of a set of 2D coordinates using Andrew's monotone chain algorithm."""
    # Deduplicate and sort points lexicographically (by lat, then lng)
    unique_points = sorted(list(set(points)))
    if len(unique_points) <= 1:
        return unique_points
    
    # 2D cross product of OA and OB vectors
    # Returns positive if counter-clockwise, negative if clockwise, zero if collinear
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    # Build lower hull
    lower = []
    for p in unique_points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
        
    # Build upper hull
    upper = []
    for p in reversed(unique_points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
        
    # Remove last point of each list because it's repeated
    return lower[:-1] + upper[:-1]


class MapGISService:
    """Handles spatial queries, coordinates clustering, hotspots prediction, and NL search parsing."""

    @staticmethod
    def get_complaints(db: Session, category: str = None, severity: str = None, status: str = None, ward: str = None) -> list[dict]:
        """Dynamic complaints query with filters."""
        query = db.query(Complaint)
        if category:
            query = query.filter(Complaint.category == category)
        if severity:
            query = query.filter(Complaint.severity == severity)
        if status:
            query = query.filter(Complaint.status == status)
        if ward:
            query = query.filter(Complaint.ward == ward)
        
        results = query.all()
        return [
            {
                "id": c.id,
                "category": c.category.value,
                "description": c.description,
                "ward": c.ward,
                "severity": c.severity.value,
                "status": c.status.value,
                "lat": c.lat,
                "lng": c.lng,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "assigned_department": c.assigned_department,
                "resolution_hours": c.resolution_hours
            }
            for c in results
        ]

    @staticmethod
    def get_resources(db: Session, rtype: str = None, status: str = None, ward: str = None) -> list[dict]:
        """Dynamic resources query with filters."""
        query = db.query(Resource)
        if rtype:
            query = query.filter(Resource.type == rtype)
        if status:
            query = query.filter(Resource.status == status)
        if ward:
            query = query.filter(Resource.ward == ward)
            
        results = query.all()
        return [
            {
                "id": r.id,
                "type": r.type.value,
                "name": r.name,
                "status": r.status.value,
                "ward": r.ward,
                "lat": r.lat,
                "lng": r.lng,
                "last_deployed": r.last_deployed.isoformat() if r.last_deployed else None
            }
            for r in results
        ]

    @staticmethod
    def get_heatmap(db: Session) -> list[list[float]]:
        """Dynamic heatmap coordinates weighted by severity."""
        complaints = db.query(Complaint).all()
        
        weight_map = {
            Severity.CRITICAL: 1.0,
            Severity.HIGH: 0.7,
            Severity.MEDIUM: 0.4,
            Severity.LOW: 0.2
        }
        
        heatmap_data = []
        for c in complaints:
            if c.lat is not None and c.lng is not None:
                weight = weight_map.get(c.severity, 0.4)
                heatmap_data.append([c.lat, c.lng, weight])
                
        return heatmap_data

    @staticmethod
    def get_wards(db: Session) -> list[dict]:
        """Dynamic ward polygon boundaries computed via convex hulls or bounding boxes."""
        # Get baseline risk indicators from MapService
        wards_metadata = MapService.get_map_data(db)
        
        # Load all complaints and resources to assign coordinates to wards
        complaints = db.query(Complaint.ward, Complaint.lat, Complaint.lng).all()
        resources = db.query(Resource.ward, Resource.lat, Resource.lng).filter(Resource.lat.isnot(None), Resource.lng.isnot(None)).all()
        
        # Group coordinates by ward
        ward_points: dict[str, list[tuple[float, float]]] = {}
        for w in WARD_COORDS.keys():
            ward_points[w] = []
            
        for c in complaints:
            if c.ward in ward_points and c.lat is not None and c.lng is not None:
                ward_points[c.ward].append((c.lat, c.lng))
                
        for r in resources:
            if r.ward in ward_points and r.lat is not None and r.lng is not None:
                ward_points[r.ward].append((r.lat, r.lng))
                
        result = []
        for w_meta in wards_metadata:
            ward_name = w_meta["name"]
            points = ward_points.get(ward_name, [])
            
            # Compute boundary coordinates
            coords = []
            if len(points) >= 3:
                # Convex Hull
                coords = convex_hull(points)
                # Ensure loop is closed for Leaflet drawing
                if coords and coords[0] != coords[-1]:
                    coords.append(coords[0])
            
            # If convex hull is too thin or points < 3, fallback to a small box around the center coordinate
            if len(coords) < 3:
                center_lat, center_lng = WARD_COORDS.get(ward_name, (BASE_LAT, BASE_LNG))
                pad = 0.0075
                coords = [
                    (center_lat - pad, center_lng - pad),
                    (center_lat + pad, center_lng - pad),
                    (center_lat + pad, center_lng + pad),
                    (center_lat - pad, center_lng + pad),
                    (center_lat - pad, center_lng - pad) # Close loop
                ]
                
            result.append({
                "name": ward_name,
                "coordinates": [[lat, lng] for lat, lng in coords],
                "risk": w_meta["risk"],
                "score": w_meta["score"],
                "details": w_meta["details"]
            })
            
        return result

    @staticmethod
    def get_predictions(db: Session) -> list[dict]:
        """Calculates predicted risk hotspots using spatial grid trends, weather conditions, and resource limits."""
        # 1. Grab all open/escalated complaints
        active_complaints = db.query(Complaint).filter(Complaint.status != ComplaintStatus.RESOLVED).all()
        
        # 2. Latest Weather multiplier
        weather = WeatherRepository.get_latest(db)
        precip = weather.precipitation_mm if weather else 0.0
        wind = weather.wind_speed_kmh if weather else 0.0
        
        # 3. Aggregate complaints in lat/lng grid buckets (approx 1.1km grid spacing)
        # grid key: (lat_bucket, lng_bucket)
        grid: dict[tuple[int, int], list[Complaint]] = {}
        for c in active_complaints:
            if c.lat is not None and c.lng is not None:
                # 2 decimal places = ~1.1km resolution
                lat_bucket = int(round(c.lat, 2) * 100)
                lng_bucket = int(round(c.lng, 2) * 100)
                bucket = (lat_bucket, lng_bucket)
                if bucket not in grid:
                    grid[bucket] = []
                grid[bucket].append(c)
                
        # 4. Score each grid cell
        hotspots = []
        severity_weight = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 3.5,
            Severity.MEDIUM: 2,
            Severity.LOW: 1
        }
        
        for bucket, complaints in grid.items():
            base_score = sum(severity_weight.get(c.severity, 2) for c in complaints)
            
            # Category counts
            flood_count = sum(1 for c in complaints if c.category == ComplaintCategory.FLOOD)
            power_count = sum(1 for c in complaints if c.category == ComplaintCategory.POWER_OUTAGE)
            garbage_count = sum(1 for c in complaints if c.category == ComplaintCategory.GARBAGE)
            
            # Weather triggers
            weather_mult = 1.0
            reasons = []
            
            if precip > 10 and flood_count > 0:
                weather_mult += 0.5 + (precip / 100.0) # Escalates based on rainfall mm
                reasons.append(f"Rainfall ({precip}mm) exacerbates {flood_count} flood risks")
                
            if wind > 25 and power_count > 0:
                weather_mult += 0.4
                reasons.append(f"High wind speeds ({wind}km/h) threaten electrical grids")
                
            if garbage_count > 3:
                reasons.append(f"Concentrated waste accumulation ({garbage_count} reports)")
                
            # Resource strain check in the cell ward
            ward_names = list(set(c.ward for c in complaints))
            primary_ward = ward_names[0] if ward_names else "Ward 1"
            
            # Resources count in primary ward
            res_avail = db.query(Resource).filter(Resource.ward == primary_ward, Resource.status == ResourceStatus.AVAILABLE).count()
            res_total = db.query(Resource).filter(Resource.ward == primary_ward).count()
            
            resource_ratio = res_avail / max(res_total, 1)
            if resource_ratio < 0.25:
                weather_mult += 0.3
                reasons.append(f"Severe resource deficit in {primary_ward} (available: {res_avail}/{res_total})")
            elif resource_ratio < 0.5:
                weather_mult += 0.15
                reasons.append(f"Resource shortage in {primary_ward}")
                
            final_risk = min(100, int(base_score * weather_mult))
            
            # Only count as hotspot if final risk score is elevated (e.g. >= 20)
            if final_risk >= 20:
                center_lat = (bucket[0] / 100.0)
                center_lng = (bucket[1] / 100.0)
                
                reason_str = "; ".join(reasons) if reasons else f"Concentration of {len(complaints)} issues"
                
                hotspots.append({
                    "lat": center_lat,
                    "lng": center_lng,
                    "radius": 500 + min(final_risk * 10, 800), # radius in meters (500m to 1500m)
                    "risk_score": final_risk,
                    "reason": reason_str,
                    "ward": primary_ward
                })
                
        # Sort hotspots by highest risk first
        hotspots.sort(key=lambda x: -x["risk_score"])
        return hotspots[:10] # Return top 10 hotspots

    @staticmethod
    def search_map(db: Session, query: str) -> dict:
        """Parses natural language input using Google Gemini (or local fallback) and returns matching database targets."""
        from ai.services import AIService
        
        parsed_filters = None
        model = AIService._get_model()
        
        if model:
            prompt = (
                "You are an AI assistant parsing natural language queries for a smart city dashboard database.\n"
                f"Parse the following query: '{query}'\n\n"
                "Identify database filter criteria for complaints and resources. The database fields and allowed values are:\n"
                "- complaint_category: 'Flood', 'Garbage', 'Traffic', 'Water Leakage', 'Power Outage', 'Street Light', 'Road Damage', 'Medical Emergency', 'Sewage' (exact match only)\n"
                "- complaint_severity: 'Low', 'Medium', 'High', 'Critical' (exact match only)\n"
                "- complaint_status: 'Open', 'In Progress', 'Resolved', 'Escalated' (exact match only)\n"
                "- resource_type: 'Garbage Truck', 'Fire Truck', 'Ambulance', 'Water Pump', 'Police Vehicle', 'Staff' (exact match only)\n"
                "- resource_status: 'Available', 'Deployed', 'Maintenance', 'Out of Service' (exact match only)\n"
                "- ward: A ward name like 'Ward 1', 'Ward 2', ..., 'Ward 20' (exact match only)\n"
                "- text_search: any general text query for description search\n\n"
                "Return a JSON object with the following fields (use null if not mentioned or not applicable):\n"
                "{\n"
                "  \"complaint_category\": string or null,\n"
                "  \"complaint_severity\": string or null,\n"
                "  \"complaint_status\": string or null,\n"
                "  \"resource_type\": string or null,\n"
                "  \"resource_status\": string or null,\n"
                "  \"ward\": string or null,\n"
                "  \"text_search\": string or null\n"
                "}\n"
                "Return ONLY the raw JSON object, without any markdown codeblock formatting or extra text."
            )
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                parsed_filters = json.loads(response.text)
            except Exception as e:
                logger.error(f"Gemini parsing failed, falling back: {e}")
                
        if not parsed_filters:
            parsed_filters = MapGISService._fallback_parse_query(query)
            
        logger.info(f"Structured filters parsed: {parsed_filters}")
        
        # Execute queries based on parsed filters
        complaints_query = db.query(Complaint)
        resources_query = db.query(Resource)
        
        # Filter complaints
        if parsed_filters.get("complaint_category"):
            complaints_query = complaints_query.filter(Complaint.category == parsed_filters["complaint_category"])
        if parsed_filters.get("complaint_severity"):
            complaints_query = complaints_query.filter(Complaint.severity == parsed_filters["complaint_severity"])
        if parsed_filters.get("complaint_status"):
            complaints_query = complaints_query.filter(Complaint.status == parsed_filters["complaint_status"])
        if parsed_filters.get("ward"):
            complaints_query = complaints_query.filter(Complaint.ward == parsed_filters["ward"])
        if parsed_filters.get("text_search"):
            complaints_query = complaints_query.filter(Complaint.description.ilike(f"%{parsed_filters['text_search']}%"))
            
        # Filter resources
        if parsed_filters.get("resource_type"):
            resources_query = resources_query.filter(Resource.type == parsed_filters["resource_type"])
        if parsed_filters.get("resource_status"):
            resources_query = resources_query.filter(Resource.status == parsed_filters["resource_status"])
        if parsed_filters.get("ward"):
            resources_query = resources_query.filter(Resource.ward == parsed_filters["ward"])
            
        # Execute (limit to prevent large payload size in search results)
        complaints = complaints_query.limit(100).all()
        resources = resources_query.limit(50).all()
        
        return {
            "filters": parsed_filters,
            "complaints": [
                {
                    "id": c.id,
                    "category": c.category.value,
                    "description": c.description,
                    "ward": c.ward,
                    "severity": c.severity.value,
                    "status": c.status.value,
                    "lat": c.lat,
                    "lng": c.lng,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in complaints
            ],
            "resources": [
                {
                    "id": r.id,
                    "type": r.type.value,
                    "name": r.name,
                    "status": r.status.value,
                    "ward": r.ward,
                    "lat": r.lat,
                    "lng": r.lng
                }
                for r in resources
            ]
        }

    @staticmethod
    def get_nearby_resources(db: Session, lat: float, lng: float, radius_km: float = 5.0, rtype: str = None) -> list[dict]:
        """Calculates distance from (lat, lng) to resources and returns matches within radius (Euclidean distance approximation)."""
        query = db.query(Resource).filter(Resource.lat.isnot(None), Resource.lng.isnot(None))
        if rtype:
            query = query.filter(Resource.type == rtype)
            
        resources = query.all()
        nearby = []
        
        for r in resources:
            # 1 degree lat ≈ 111km, 1 degree lng ≈ 111km * cos(lat)
            # Standard Euclidean conversion:
            dx = (r.lat - lat) * 111.0
            dy = (r.lng - lng) * 111.0 * math.cos(math.radians(lat))
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= radius_km:
                nearby.append({
                    "id": r.id,
                    "type": r.type.value,
                    "name": r.name,
                    "status": r.status.value,
                    "ward": r.ward,
                    "lat": r.lat,
                    "lng": r.lng,
                    "distance_km": round(dist, 2)
                })
                
        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])
        return nearby

    @staticmethod
    def _fallback_parse_query(query: str) -> dict:
        """Rule-based local parser to extract entities from query if Gemini is unavailable."""
        q_lower = query.lower()
        filters = {
            "complaint_category": None,
            "complaint_severity": None,
            "complaint_status": None,
            "resource_type": None,
            "resource_status": None,
            "ward": None,
            "text_search": None
        }
        
        # Ward lookup
        for i in range(1, 21):
            if f"ward {i}" in q_lower:
                filters["ward"] = f"Ward {i}"
                break
                
        # Severity lookup
        for sev in Severity:
            if sev.value.lower() in q_lower:
                filters["complaint_severity"] = sev.value
                break
                
        # Status lookup
        for status in ComplaintStatus:
            if status.value.lower() in q_lower:
                filters["complaint_status"] = status.value
                break
                
        # Category lookup
        for cat in ComplaintCategory:
            if cat.value.lower() in q_lower:
                filters["complaint_category"] = cat.value
                break
                
        # Resource Type lookup
        for rtype in ResourceType:
            if rtype.value.lower() in q_lower:
                filters["resource_type"] = rtype.value
                break
                
        # Resource Status lookup
        for rstatus in ResourceStatus:
            if rstatus.value.lower() in q_lower:
                filters["resource_status"] = rstatus.value
                break
                
        # Extract leftover description / search term
        # If no explicit category is found, put the key query as text search
        words = q_lower.split()
        stopwords = {"find", "all", "show", "me", "near", "in", "at", "the", "on", "active", "open", "issues", "complaints", "resources"}
        cleaned_words = [w for w in words if w not in stopwords and not w.startswith("ward")]
        
        if cleaned_words:
            filters["text_search"] = " ".join(cleaned_words)
            
        return filters
