"""
Analytics router — serves SQL-computed analytics from PostgreSQL.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Return analytics data computed from PostgreSQL queries."""
    start = time.perf_counter()
    data = AnalyticsService.get_analytics_data(db)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": "Analytics data loaded",
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }
