"""add public holding to fundamental snapshots

Revision ID: 20260609_0003
Revises: 20260608_0002
Create Date: 2026-06-09
"""

from alembic import op
import sqlalchemy as sa

revision = "20260609_0003"
down_revision = "20260608_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("fundamental_snapshots", sa.Column("public_holding_pct", sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("fundamental_snapshots", "public_holding_pct")
