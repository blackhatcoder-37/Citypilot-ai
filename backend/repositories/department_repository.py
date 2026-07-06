"""
Department repository — all database queries for departments.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Department, Complaint


class DepartmentRepository:
    """Data-access layer for the departments table."""

    @staticmethod
    def get_all(db: Session) -> list[Department]:
        return db.query(Department).all()

    @staticmethod
    def get_count(db: Session) -> int:
        return db.query(func.count(Department.id)).scalar() or 0

    @staticmethod
    def get_performance_stats(db: Session) -> list[dict]:
        """Department performance metrics based on complaint resolution data."""
        rows = (
            db.query(
                Complaint.assigned_department,
                func.count(Complaint.id).label("total"),
                func.avg(Complaint.resolution_hours).label("avg_resolution_hours"),
                func.count(
                    Complaint.id
                ).filter(Complaint.status == "Resolved").label("resolved_count"),
            )
            .filter(Complaint.assigned_department.isnot(None))
            .group_by(Complaint.assigned_department)
            .all()
        )

        if not rows:
            return [
                {"subject": "Response Time", "score": 0, "fullMark": 150},
                {"subject": "Resolution", "score": 0, "fullMark": 150},
                {"subject": "Efficiency", "score": 0, "fullMark": 150},
                {"subject": "Citizen Sat.", "score": 0, "fullMark": 150},
                {"subject": "Proactivity", "score": 0, "fullMark": 150},
                {"subject": "Cost Mgmt", "score": 0, "fullMark": 150},
            ]

        # Aggregate across all departments into normalised radar-chart scores
        total_complaints = sum(r.total for r in rows)
        total_resolved = sum(r.resolved_count for r in rows)
        avg_res_hours_all = sum(
            float(r.avg_resolution_hours or 0) for r in rows
        ) / max(len(rows), 1)

        resolution_rate = total_resolved / max(total_complaints, 1)

        # Map real metrics → radar scores (0-150 scale)
        response_time_score = max(0, min(150, int(150 - avg_res_hours_all * 1.5)))
        resolution_score = int(resolution_rate * 150)
        efficiency_score = max(0, min(150, int(resolution_score * 0.9)))
        citizen_sat_score = max(0, min(150, int(resolution_score * 0.95)))
        proactivity_score = max(0, min(150, int(150 - avg_res_hours_all)))
        cost_mgmt_score = max(0, min(150, int(efficiency_score * 0.75)))

        return [
            {"subject": "Response Time", "score": response_time_score, "fullMark": 150},
            {"subject": "Resolution", "score": resolution_score, "fullMark": 150},
            {"subject": "Efficiency", "score": efficiency_score, "fullMark": 150},
            {"subject": "Citizen Sat.", "score": citizen_sat_score, "fullMark": 150},
            {"subject": "Proactivity", "score": proactivity_score, "fullMark": 150},
            {"subject": "Cost Mgmt", "score": cost_mgmt_score, "fullMark": 150},
        ]
