"""
Map service — calculates ward-level risk scores from PostgreSQL data.
"""

from sqlalchemy.orm import Session

from repositories.complaint_repository import ComplaintRepository
from repositories.weather_repository import WeatherRepository
from repositories.resource_repository import ResourceRepository

# Base coordinates (New Delhi, India) for wards
BASE_LAT = 28.6139
BASE_LNG = 77.2090


# Pre-defined ward center coordinates (spread around base)
WARD_COORDS: dict[str, tuple[float, float]] = {
    f"Ward {i}": (
        round(BASE_LAT + (((i - 1) % 5) - 2) * 0.012, 4),
        round(BASE_LNG + (((i - 1) // 5) - 2) * 0.012, 4),
    )
    for i in range(1, 21)
}


def _risk_label(score: int) -> str:
    """Map score (0-100) to risk colour label."""
    if score >= 70:
        return "Red"
    elif score >= 50:
        return "Orange"
    elif score >= 30:
        return "Yellow"
    return "Green"


def _resource_label(available: int, total: int) -> str:
    pct = available / max(total, 1)
    if pct >= 0.5:
        return "Available"
    elif pct >= 0.25:
        return "Strained"
    return "Depleted"


class MapService:
    """Calculates real-time ward risk using complaint, weather, and resource data."""

    @staticmethod
    def get_map_data(db: Session) -> list[dict]:
        # 1. Complaint data per ward (count + severity weighting)
        ward_complaints = {
            row["ward"]: row
            for row in ComplaintRepository.get_by_ward(db)
        }

        # 2. Latest weather
        latest_weather = WeatherRepository.get_latest(db)
        weather_condition = latest_weather.condition if latest_weather else "Clear"
        precipitation = latest_weather.precipitation_mm if latest_weather else 0.0

        # Weather risk multiplier
        weather_multiplier = 1.0
        if precipitation > 50:
            weather_multiplier = 1.5
        elif precipitation > 20:
            weather_multiplier = 1.25
        elif precipitation > 5:
            weather_multiplier = 1.1

        # 3. Resource availability per ward
        ward_resources = {
            row["ward"]: row
            for row in ResourceRepository.get_by_ward(db)
        }

        # 4. Build ward risk scores
        wards = []
        for ward_name in [f"Ward {i}" for i in range(1, 21)]:
            complaint_data = ward_complaints.get(ward_name, {"count": 0, "weighted_score": 0})
            resource_data = ward_resources.get(ward_name, {"total": 0, "available": 0})

            # Normalised complaint score (0-60 range)
            complaint_score = min(60, complaint_data["weighted_score"] / max(1, 10) * 3)

            # Resource penalty (0-20 range) — fewer available = higher risk
            resource_ratio = resource_data["available"] / max(resource_data["total"], 1)
            resource_penalty = (1 - resource_ratio) * 20

            # Base score + weather
            raw_score = (complaint_score + resource_penalty) * weather_multiplier

            # Clamp to 0-100
            score = max(0, min(100, int(raw_score)))

            lat, lng = WARD_COORDS.get(ward_name, (BASE_LAT, BASE_LNG))

            wards.append({
                "name": ward_name,
                "lat": lat,
                "lng": lng,
                "risk": _risk_label(score),
                "score": score,
                "details": {
                    "complaints": complaint_data["count"],
                    "weather": weather_condition,
                    "resources": _resource_label(
                        resource_data["available"], resource_data["total"]
                    ),
                    "population": f"{30000 + hash(ward_name) % 40000:,}",
                },
            })

        return wards
