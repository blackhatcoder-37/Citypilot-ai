"""
Dashboard router — serves live dashboard data from PostgreSQL.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Return complete dashboard data computed from PostgreSQL."""
    start = time.perf_counter()
    data = DashboardService.get_dashboard_data(db)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": "Dashboard data loaded",
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }
