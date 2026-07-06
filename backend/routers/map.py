"""
Map router — serves dynamically-computed GIS data and search capabilities.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from services.map_service import MapService
from services.map_gis_service import MapGISService

router = APIRouter()


class SearchRequest(BaseModel):
    query: str


@router.get("/map")
def get_map_data(db: Session = Depends(get_db)):
    """Return ward risk map data calculated from PostgreSQL."""
    start = time.perf_counter()
    wards = MapService.get_map_data(db)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": "Map data loaded",
        "data": {"wards": wards},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.get("/map/complaints")
def get_map_complaints(
    category: str = None,
    severity: str = None,
    status: str = None,
    ward: str = None,
    db: Session = Depends(get_db)
):
    """Retrieve complaints with optional filters."""
    start = time.perf_counter()
    complaints = MapGISService.get_complaints(db, category, severity, status, ward)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": f"Retrieved {len(complaints)} complaints",
        "data": complaints,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.get("/map/resources")
def get_map_resources(
    type: str = None,
    status: str = None,
    ward: str = None,
    db: Session = Depends(get_db)
):
    """Retrieve resources with optional filters."""
    start = time.perf_counter()
    resources = MapGISService.get_resources(db, type, status, ward)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": f"Retrieved {len(resources)} resources",
        "data": resources,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.get("/map/heatmap")
def get_heatmap_data(db: Session = Depends(get_db)):
    """Retrieve weighted coordinates for heatmap rendering."""
    start = time.perf_counter()
    points = MapGISService.get_heatmap(db)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": f"Retrieved {len(points)} heatmap points",
        "data": points,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.get("/map/wards")
def get_ward_polygons(db: Session = Depends(get_db)):
    """Retrieve ward boundary polygons calculated dynamically."""
    start = time.perf_counter()
    wards = MapGISService.get_wards(db)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": "Ward polygons loaded",
        "data": {"wards": wards},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.get("/map/predictions")
def get_predictions(db: Session = Depends(get_db)):
    """Retrieve predicted hotspots and trend risks."""
    start = time.perf_counter()
    predictions = MapGISService.get_predictions(db)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": f"Calculated {len(predictions)} prediction hotspots",
        "data": predictions,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.post("/map/search")
def search_map(req: SearchRequest, db: Session = Depends(get_db)):
    """Parse search queries and return filtered map targets."""
    start = time.perf_counter()
    result = MapGISService.search_map(db, req.query)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": "Search completed",
        "data": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }


@router.get("/map/nearby-resources")
def get_nearby_resources(
    lat: float,
    lng: float,
    radius_km: float = 5.0,
    type: str = None,
    db: Session = Depends(get_db)
):
    """Retrieve resources near specific coordinates."""
    start = time.perf_counter()
    resources = MapGISService.get_nearby_resources(db, lat, lng, radius_km, type)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": f"Found {len(resources)} nearby resources",
        "data": resources,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }

