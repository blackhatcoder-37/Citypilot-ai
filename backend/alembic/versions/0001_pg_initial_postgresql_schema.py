"""initial_postgresql_schema

Revision ID: 0001_pg_initial
Revises:
Create Date: 2026-07-03

PostgreSQL-native migration with enum types, proper indexes, and now() defaults.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_pg_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── PostgreSQL enum types ──────────────────────────────────────────

complaintcategory = sa.Enum(
    "Flood", "Garbage", "Traffic", "Water Leakage", "Power Outage",
    "Street Light", "Road Damage", "Medical Emergency", "Sewage",
    name="complaintcategory",
)

severity = sa.Enum("Low", "Medium", "High", "Critical", name="severity")

complaintstatus = sa.Enum(
    "Open", "In Progress", "Resolved", "Escalated",
    name="complaintstatus",
)

resourcetype = sa.Enum(
    "Garbage Truck", "Fire Truck", "Ambulance", "Water Pump",
    "Police Vehicle", "Staff",
    name="resourcetype",
)

resourcestatus = sa.Enum(
    "Available", "Deployed", "Maintenance", "Out of Service",
    name="resourcestatus",
)


def upgrade() -> None:
    """Create all tables with PostgreSQL-native features."""

    # ── complaints ──────────────────────────────────────────────────
    op.create_table(
        "complaints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", complaintcategory, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("ward", sa.String(20), nullable=False),
        sa.Column("severity", severity, nullable=False),
        sa.Column("status", complaintstatus, nullable=False, server_default="Open"),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("assigned_department", sa.String(100), nullable=True),
        sa.Column("resolution_hours", sa.Float(), nullable=True),
    )
    op.create_index("ix_complaints_id", "complaints", ["id"])
    op.create_index("ix_complaints_category", "complaints", ["category"])
    op.create_index("ix_complaints_ward", "complaints", ["ward"])
    op.create_index("ix_complaints_severity", "complaints", ["severity"])
    op.create_index("ix_complaints_status", "complaints", ["status"])
    op.create_index("ix_complaints_created_at", "complaints", ["created_at"])
    op.create_index("ix_complaints_category_ward", "complaints", ["category", "ward"])
    op.create_index("ix_complaints_severity_status", "complaints", ["severity", "status"])

    # ── weather ─────────────────────────────────────────────────────
    op.create_table(
        "weather",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("temperature_c", sa.Float(), nullable=False),
        sa.Column("humidity_pct", sa.Float(), nullable=False),
        sa.Column("precipitation_mm", sa.Float(), nullable=False),
        sa.Column("wind_speed_kmh", sa.Float(), nullable=False),
        sa.Column("condition", sa.String(50), nullable=False),
        sa.Column("aqi", sa.Integer(), nullable=True),
    )
    op.create_index("ix_weather_id", "weather", ["id"])
    op.create_index("ix_weather_recorded_at", "weather", ["recorded_at"], unique=True)

    # ── resources ───────────────────────────────────────────────────
    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", resourcetype, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("status", resourcestatus, nullable=False, server_default="Available"),
        sa.Column("ward", sa.String(20), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("last_deployed", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_resources_id", "resources", ["id"])
    op.create_index("ix_resources_type", "resources", ["type"])
    op.create_index("ix_resources_status", "resources", ["status"])
    op.create_index("ix_resources_ward", "resources", ["ward"])

    # ── departments ─────────────────────────────────────────────────
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("head", sa.String(100), nullable=True),
        sa.Column("contact_email", sa.String(150), nullable=True),
        sa.Column("total_staff", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_departments_id", "departments", ["id"])

    # ── chat_history ────────────────────────────────────────────────
    op.create_table(
        "chat_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_index("ix_chat_history_id", "chat_history", ["id"])
    op.create_index("ix_chat_history_timestamp", "chat_history", ["timestamp"])
    op.create_index("ix_chat_history_user_id", "chat_history", ["user_id"])

    # ── knowledge_documents ─────────────────────────────────────────
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("upload_date", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("status", sa.String(30), nullable=False, server_default="Uploaded"),
        sa.Column("is_embedded", sa.Boolean(), server_default=sa.text("false")),
    )
    op.create_index("ix_knowledge_documents_id", "knowledge_documents", ["id"])
    op.create_index("ix_knowledge_documents_upload_date", "knowledge_documents", ["upload_date"])


def downgrade() -> None:
    """Drop all tables and enum types."""
    op.drop_table("knowledge_documents")
    op.drop_table("chat_history")
    op.drop_table("departments")
    op.drop_table("resources")
    op.drop_table("weather")
    op.drop_table("complaints")

    # Drop enum types
    resourcestatus.drop(op.get_bind(), checkfirst=True)
    resourcetype.drop(op.get_bind(), checkfirst=True)
    complaintstatus.drop(op.get_bind(), checkfirst=True)
    severity.drop(op.get_bind(), checkfirst=True)
    complaintcategory.drop(op.get_bind(), checkfirst=True)
