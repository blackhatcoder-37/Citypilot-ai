"""
SQLAlchemy ORM models for CityPilot AI.
All enum columns use PostgreSQL-native enum types.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text,
    Enum as SAEnum, Boolean, Index, ForeignKey, ARRAY,
)
from sqlalchemy.sql import func
from database.database import Base
import enum


# ═══════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════

class ComplaintCategory(str, enum.Enum):
    FLOOD = "Flood"
    GARBAGE = "Garbage"
    TRAFFIC = "Traffic"
    WATER_LEAKAGE = "Water Leakage"
    POWER_OUTAGE = "Power Outage"
    STREET_LIGHT = "Street Light"
    ROAD_DAMAGE = "Road Damage"
    MEDICAL_EMERGENCY = "Medical Emergency"
    SEWAGE = "Sewage"


class Severity(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ComplaintStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"


class ResourceType(str, enum.Enum):
    GARBAGE_TRUCK = "Garbage Truck"
    FIRE_TRUCK = "Fire Truck"
    AMBULANCE = "Ambulance"
    WATER_PUMP = "Water Pump"
    POLICE_VEHICLE = "Police Vehicle"
    STAFF = "Staff"


class ResourceStatus(str, enum.Enum):
    AVAILABLE = "Available"
    DEPLOYED = "Deployed"
    MAINTENANCE = "Maintenance"
    OUT_OF_SERVICE = "Out of Service"


# ═══════════════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════════════

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(
        SAEnum(ComplaintCategory, name="complaintcategory", create_constraint=True, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    description = Column(Text, nullable=False)
    ward = Column(String(20), nullable=False, index=True)
    severity = Column(
        SAEnum(Severity, name="severity", create_constraint=True, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    status = Column(
        SAEnum(ComplaintStatus, name="complaintstatus", create_constraint=True, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ComplaintStatus.OPEN,
        index=True,
    )
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    assigned_department = Column(String(100), nullable=True)
    resolution_hours = Column(Float, nullable=True)

    __table_args__ = (
        Index("ix_complaints_category_ward", "category", "ward"),
        Index("ix_complaints_severity_status", "severity", "status"),
        Index("ix_complaints_lat_lng", "lat", "lng"),
    )


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True, unique=True)
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    precipitation_mm = Column(Float, nullable=False)
    wind_speed_kmh = Column(Float, nullable=False)
    condition = Column(String(50), nullable=False)
    aqi = Column(Integer, nullable=True)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(
        SAEnum(ResourceType, name="resourcetype", create_constraint=True, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    status = Column(
        SAEnum(ResourceStatus, name="resourcestatus", create_constraint=True, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ResourceStatus.AVAILABLE,
        index=True,
    )
    ward = Column(String(20), nullable=False, index=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    last_deployed = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_resources_lat_lng", "lat", "lng"),
    )


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    head = Column(String(100), nullable=True)
    contact_email = Column(String(150), nullable=True)
    total_staff = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(Integer, nullable=True, index=True)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    status = Column(String(30), nullable=False, default="Uploaded")
    is_embedded = Column(Boolean, default=False)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    source_filename = Column(String(255), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)

