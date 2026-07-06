"""
Resource repository — all database queries for resources.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case

from database.models import Resource, ResourceStatus, ResourceType


class ResourceRepository:
    """Data-access layer for the resources table."""

    @staticmethod
    def get_all(db: Session) -> list[Resource]:
        return db.query(Resource).all()

    @staticmethod
    def get_available_count(db: Session) -> int:
        return (
            db.query(func.count(Resource.id))
            .filter(Resource.status == ResourceStatus.AVAILABLE)
            .scalar()
        ) or 0

    @staticmethod
    def get_total_count(db: Session) -> int:
        return db.query(func.count(Resource.id)).scalar() or 0

    @staticmethod
    def get_utilization(db: Session) -> list[dict]:
        """Resource utilization grouped by type — deployed vs available."""
        rows = (
            db.query(
                Resource.type,
                func.count(
                    case((Resource.status == ResourceStatus.DEPLOYED, Resource.id))
                ).label("used"),
                func.count(
                    case((Resource.status == ResourceStatus.AVAILABLE, Resource.id))
                ).label("available"),
            )
            .group_by(Resource.type)
            .all()
        )

        # Friendly display names
        type_labels = {
            ResourceType.AMBULANCE: "Ambulances",
            ResourceType.FIRE_TRUCK: "Fire Trucks",
            ResourceType.WATER_PUMP: "Water Pumps",
            ResourceType.POLICE_VEHICLE: "Police",
            ResourceType.GARBAGE_TRUCK: "Garbage Trucks",
            ResourceType.STAFF: "Staff",
        }

        return [
            {
                "name": type_labels.get(row.type, row.type.value),
                "used": row.used,
                "available": row.available,
            }
            for row in rows
        ]

    @staticmethod
    def get_utilization_pct(db: Session) -> list[dict]:
        """Resource utilization percentages vs target for analytics."""
        rows = (
            db.query(
                Resource.type,
                func.count(Resource.id).label("total"),
                func.count(
                    case((Resource.status == ResourceStatus.DEPLOYED, Resource.id))
                ).label("deployed"),
            )
            .group_by(Resource.type)
            .all()
        )

        type_labels = {
            ResourceType.AMBULANCE: "Ambulances",
            ResourceType.FIRE_TRUCK: "Fire Trucks",
            ResourceType.WATER_PUMP: "Water Pumps",
            ResourceType.POLICE_VEHICLE: "Police",
            ResourceType.GARBAGE_TRUCK: "Garbage",
            ResourceType.STAFF: "Staff",
        }

        targets = {
            ResourceType.AMBULANCE: 85,
            ResourceType.FIRE_TRUCK: 70,
            ResourceType.WATER_PUMP: 80,
            ResourceType.POLICE_VEHICLE: 75,
            ResourceType.GARBAGE_TRUCK: 90,
            ResourceType.STAFF: 85,
        }

        return [
            {
                "name": type_labels.get(row.type, row.type.value),
                "utilized": round(row.deployed / max(row.total, 1) * 100),
                "target": targets.get(row.type, 80),
            }
            for row in rows
        ]

    @staticmethod
    def get_by_ward(db: Session) -> list[dict]:
        """Count resources by ward."""
        rows = (
            db.query(
                Resource.ward,
                func.count(Resource.id).label("total"),
                func.count(
                    case((Resource.status == ResourceStatus.AVAILABLE, Resource.id))
                ).label("available"),
            )
            .group_by(Resource.ward)
            .all()
        )
        return [
            {"ward": row.ward, "total": row.total, "available": row.available}
            for row in rows
        ]
