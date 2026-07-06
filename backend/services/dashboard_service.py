"""
Dashboard service — aggregates all dashboard data from PostgreSQL.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from repositories.complaint_repository import ComplaintRepository
from repositories.weather_repository import WeatherRepository
from repositories.resource_repository import ResourceRepository
from ai.services import AIService


class DashboardService:
    """Builds the complete dashboard payload from live database queries."""

    @staticmethod
    def get_dashboard_data(db: Session) -> dict:
        # ── Top cards ───────────────────────────────────────────────
        active_complaints = ComplaintRepository.get_active_count(db)
        critical_areas = ComplaintRepository.get_critical_count(db)
        total_resources = ResourceRepository.get_total_count(db)
        available_resources = ResourceRepository.get_available_count(db)
        resources_pct = round(available_resources / max(total_resources, 1) * 100)

        # ── AI Insights ─────────────────────────────────────────────
        insights = AIService.get_insights(db)

        top_cards = {
            "active_complaints": active_complaints,
            "critical_areas": critical_areas,
            "resources_available": resources_pct,
            "today_ai_insights": len(insights),
        }

        # ── Charts ──────────────────────────────────────────────────
        complaint_trend = ComplaintRepository.get_trend_by_day(db, days=7)
        risk_distribution = ComplaintRepository.get_severity_distribution(db)
        weather_trend = WeatherRepository.get_trend(db, days=7)
        resource_usage = ResourceRepository.get_utilization(db)

        charts = {
            "complaint_trend": complaint_trend,
            "risk_distribution": risk_distribution,
            "weather_trend": weather_trend,
            "resource_usage": resource_usage,
        }

        # ── Recent incidents ────────────────────────────────────────
        recent_complaints = ComplaintRepository.get_recent(db, limit=4)
        recent_incidents = []
        for c in recent_complaints:
            now = datetime.now(timezone.utc)
            delta = now - c.created_at.replace(tzinfo=timezone.utc) if c.created_at.tzinfo is None else now - c.created_at
            minutes = int(delta.total_seconds() / 60)
            if minutes < 60:
                time_str = f"{minutes} min ago"
            elif minutes < 1440:
                time_str = f"{minutes // 60} hr ago"
            else:
                time_str = f"{minutes // 1440} days ago"

            recent_incidents.append({
                "id": c.id,
                "title": c.description[:60] + ("..." if len(c.description) > 60 else ""),
                "location": c.ward,
                "status": c.severity.value,
                "time": time_str,
                "category": c.category.value,
            })

        return {
            "top_cards": top_cards,
            "charts": charts,
            "recent_incidents": recent_incidents,
            "insights": insights,
        }
