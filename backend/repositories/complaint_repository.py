"""
Complaint repository — all database queries for complaints.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract, text

from database.models import Complaint, ComplaintStatus, Severity


class ComplaintRepository:
    """Data-access layer for the complaints table."""

    # ── Counts ──────────────────────────────────────────────────────

    @staticmethod
    def get_active_count(db: Session) -> int:
        """Count complaints that are not resolved."""
        return (
            db.query(func.count(Complaint.id))
            .filter(Complaint.status != ComplaintStatus.RESOLVED)
            .scalar()
        ) or 0

    @staticmethod
    def get_critical_count(db: Session) -> int:
        """Count complaints with Critical severity that are still open/escalated."""
        return (
            db.query(func.count(Complaint.id))
            .filter(
                Complaint.severity == Severity.CRITICAL,
                Complaint.status.in_([ComplaintStatus.OPEN, ComplaintStatus.ESCALATED]),
            )
            .scalar()
        ) or 0

    @staticmethod
    def get_open_count(db: Session) -> int:
        return (
            db.query(func.count(Complaint.id))
            .filter(Complaint.status == ComplaintStatus.OPEN)
            .scalar()
        ) or 0

    @staticmethod
    def get_total_count(db: Session) -> int:
        return db.query(func.count(Complaint.id)).scalar() or 0

    # ── Trend / Chart data ──────────────────────────────────────────

    @staticmethod
    def get_trend_by_day(db: Session, days: int = 7) -> list[dict]:
        """Daily complaint counts and resolved counts for the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        rows = (
            db.query(
                func.date_trunc("day", Complaint.created_at).label("day"),
                func.count(Complaint.id).label("complaints"),
                func.count(
                    case(
                        (Complaint.status == ComplaintStatus.RESOLVED, Complaint.id),
                    )
                ).label("resolved"),
            )
            .filter(Complaint.created_at >= cutoff)
            .group_by(text("day"))
            .order_by(text("day"))
            .all()
        )
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return [
            {
                "day": day_names[row.day.weekday()] if row.day else "N/A",
                "complaints": row.complaints,
                "resolved": row.resolved,
            }
            for row in rows
        ]

    @staticmethod
    def get_severity_distribution(db: Session) -> list[dict]:
        """Count complaints grouped by severity."""
        rows = (
            db.query(
                Complaint.severity,
                func.count(Complaint.id).label("value"),
            )
            .group_by(Complaint.severity)
            .all()
        )
        return [{"name": row.severity.value, "value": row.value} for row in rows]

    @staticmethod
    def get_status_distribution(db: Session) -> list[dict]:
        """Count complaints grouped by status."""
        rows = (
            db.query(
                Complaint.status,
                func.count(Complaint.id).label("count"),
            )
            .group_by(Complaint.status)
            .all()
        )
        return [{"name": row.status.value, "count": row.count} for row in rows]

    @staticmethod
    def get_recent(db: Session, limit: int = 10) -> list[Complaint]:
        """Most recent complaints ordered by created_at desc."""
        return (
            db.query(Complaint)
            .order_by(Complaint.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_ward(db: Session) -> list[dict]:
        """Complaint count per ward with severity weighting."""
        rows = (
            db.query(
                Complaint.ward,
                func.count(Complaint.id).label("count"),
                func.sum(
                    case(
                        (Complaint.severity == Severity.CRITICAL, 4),
                        (Complaint.severity == Severity.HIGH, 3),
                        (Complaint.severity == Severity.MEDIUM, 2),
                        (Complaint.severity == Severity.LOW, 1),
                        else_=1,
                    )
                ).label("weighted_score"),
            )
            .group_by(Complaint.ward)
            .all()
        )
        return [
            {"ward": row.ward, "count": row.count, "weighted_score": int(row.weighted_score or 0)}
            for row in rows
        ]

    @staticmethod
    def get_category_trend(db: Session, months: int = 6) -> list[dict]:
        """Monthly complaint counts per category for the last N months."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)
        rows = (
            db.query(
                extract("month", Complaint.created_at).label("month"),
                Complaint.category,
                func.count(Complaint.id).label("count"),
            )
            .filter(Complaint.created_at >= cutoff)
            .group_by(extract("month", Complaint.created_at), Complaint.category)
            .order_by(extract("month", Complaint.created_at))
            .all()
        )

        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        # Pivot into {month: {category: count}}
        pivot: dict[int, dict] = {}
        for row in rows:
            m = int(row._mapping["month"])
            if m not in pivot:
                pivot[m] = {"name": month_names[m]}
            pivot[m][row.category.value.replace(" ", "_")] = row._mapping["count"]

        return list(pivot.values())

    @staticmethod
    def get_weekly_comparison(db: Session) -> list[dict]:
        """Compare this week vs last week complaint counts per day-of-week."""
        now = datetime.now(timezone.utc)
        this_week_start = now - timedelta(days=now.weekday())
        last_week_start = this_week_start - timedelta(days=7)

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        def _week_counts(start: datetime, end: datetime) -> dict[int, int]:
            rows = (
                db.query(
                    extract("isodow", Complaint.created_at).label("dow"),
                    func.count(Complaint.id).label("count"),
                )
                .filter(Complaint.created_at >= start, Complaint.created_at < end)
                .group_by(extract("isodow", Complaint.created_at))
                .all()
            )
            return {int(r._mapping["dow"]): int(r._mapping["count"]) for r in rows}

        this_week = _week_counts(this_week_start, now)
        last_week = _week_counts(last_week_start, this_week_start)

        return [
            {
                "day": day_names[i],
                "thisWeek": this_week.get(i + 1, 0),
                "lastWeek": last_week.get(i + 1, 0),
            }
            for i in range(7)
        ]

    @staticmethod
    def get_by_id(db: Session, complaint_id: int) -> Complaint | None:
        return db.query(Complaint).filter(Complaint.id == complaint_id).first()

    @staticmethod
    def create(db: Session, complaint: Complaint) -> Complaint:
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return complaint

    @staticmethod
    def get_affected_wards(db: Session, limit: int = 5) -> list[str]:
        """Wards with the most open/escalated complaints."""
        rows = (
            db.query(Complaint.ward, func.count(Complaint.id).label("cnt"))
            .filter(Complaint.status.in_([ComplaintStatus.OPEN, ComplaintStatus.ESCALATED]))
            .group_by(Complaint.ward)
            .order_by(func.count(Complaint.id).desc())
            .limit(limit)
            .all()
        )
        return [row.ward for row in rows]
