"""
Settings service — reports PostgreSQL connection health and metadata.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text

from config import get_settings


class SettingsService:
    """Checks PostgreSQL health, version, and pool status."""

    @staticmethod
    def get_system_status(db: Session) -> dict:
        settings = get_settings()

        # ── PostgreSQL version ──────────────────────────────────────
        db_version = "Unknown"
        db_status = "Disconnected"
        try:
            row = db.execute(text("SELECT version()")).fetchone()
            if row:
                db_version = row[0].split(",")[0]  # e.g. "PostgreSQL 16.3"
                db_status = "Healthy"
        except Exception:
            db_status = "Error"

        # Check Gemini API Key existence
        import os
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        ai_engine = "Google Gemini (Connected)" if api_key else "Google Gemini (Missing Key)"

        return {
            "api_status": "Connected",
            "database_type": "PostgreSQL",
            "database_status": db_status,
            "database_version": db_version,
            "connection_pool_size": settings.DB_POOL_SIZE,
            "ai_engine": ai_engine,
            "app_version": settings.APP_VERSION,
        }
