"""add_gis_indexes

Revision ID: 0002_add_gis_indexes
Revises: 0001_pg_initial
Create Date: 2026-07-04

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_gis_indexes"
down_revision: Union[str, Sequence[str], None] = "0001_pg_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create composite index on complaints (lat, lng)
    op.create_index("ix_complaints_lat_lng", "complaints", ["lat", "lng"])
    # Create composite index on resources (lat, lng)
    op.create_index("ix_resources_lat_lng", "resources", ["lat", "lng"])

def downgrade() -> None:
    op.drop_index("ix_complaints_lat_lng", table_name="complaints")
    op.drop_index("ix_resources_lat_lng", table_name="resources")
