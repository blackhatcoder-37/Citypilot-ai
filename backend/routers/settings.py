"""
Settings router — returns PostgreSQL health and system status.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from services.settings_service import SettingsService

router = APIRouter()


@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    """Return system status including PostgreSQL health and version."""
    start = time.perf_counter()
    data = SettingsService.get_system_status(db)
    elapsed = round((time.perf_counter() - start) * 1000, 2)

    return {
        "success": True,
        "message": "System status retrieved",
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_time_ms": elapsed,
    }
