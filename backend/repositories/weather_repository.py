"""
Weather repository — all database queries for weather records.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta, timezone

from database.models import Weather


class WeatherRepository:
    """Data-access layer for the weather table."""

    @staticmethod
    def get_latest(db: Session) -> Weather | None:
        """Return the most recent weather record."""
        return (
            db.query(Weather)
            .order_by(Weather.recorded_at.desc())
            .first()
        )

    @staticmethod
    def get_recent(db: Session, days: int = 7) -> list[Weather]:
        """Return weather records for the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            db.query(Weather)
            .filter(Weather.recorded_at >= cutoff)
            .order_by(Weather.recorded_at.asc())
            .all()
        )

    @staticmethod
    def get_trend(db: Session, days: int = 7) -> list[dict]:
        """Daily temperature and precipitation for charts."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        rows = (
            db.query(
                func.date_trunc("day", Weather.recorded_at).label("day"),
                func.avg(Weather.temperature_c).label("temp"),
                func.max(Weather.precipitation_mm).label("rain"),
            )
            .filter(Weather.recorded_at >= cutoff)
            .group_by(text("day"))
            .order_by(text("day"))
            .all()
        )
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return [
            {
                "day": day_names[row.day.weekday()] if row.day else "N/A",
                "temp": round(float(row.temp or 0), 1),
                "rain": round(float(row.rain or 0), 1),
            }
            for row in rows
        ]

    @staticmethod
    def get_count(db: Session) -> int:
        return db.query(func.count(Weather.id)).scalar() or 0
