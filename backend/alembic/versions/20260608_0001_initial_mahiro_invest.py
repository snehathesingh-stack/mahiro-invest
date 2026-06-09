"""initial Mahiro Invest schema

Revision ID: 20260608_0001
Revises:
Create Date: 2026-06-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260608_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "stocks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("company_name", sa.String(200), nullable=False),
        sa.Column("sector", sa.String(100)),
        sa.Column("market_cap", sa.Numeric(20, 2)),
        sa.Column("last_price", sa.Numeric(15, 2)),
        sa.Column("last_updated", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_stocks_symbol", "stocks", ["symbol"], unique=True)

    op.create_table(
        "personas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500)),
        sa.Column("criteria", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "holdings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Numeric(15, 4), nullable=False),
        sa.Column("avg_buy_price", sa.Numeric(15, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("stock_ids", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "fundamental_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("pe_ratio", sa.Numeric(10, 2)),
        sa.Column("eps", sa.Numeric(10, 2)),
        sa.Column("roe", sa.Numeric(10, 2)),
        sa.Column("debt_to_equity", sa.Numeric(10, 2)),
        sa.Column("revenue_growth_yoy", sa.Numeric(10, 2)),
        sa.Column("profit_margin", sa.Numeric(10, 2)),
        sa.Column("cash_flow_from_operations", sa.Numeric(20, 2)),
        sa.Column("cash_flow_positive", sa.Boolean()),
        sa.Column("debtor_days", sa.Numeric(10, 2)),
        sa.Column("fii_holding_pct", sa.Numeric(10, 2)),
        sa.Column("dii_holding_pct", sa.Numeric(10, 2)),
        sa.Column("public_holding_pct", sa.Numeric(10, 2)),
        sa.Column("moving_avg_20d", sa.Numeric(15, 2)),
        sa.Column("moving_avg_200d", sa.Numeric(15, 2)),
        sa.Column("dividend_yield", sa.Numeric(10, 2)),
        sa.Column("raw_json", postgresql.JSONB()),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("fetched_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("fundamental_snapshots")
    op.drop_table("watchlists")
    op.drop_table("holdings")
    op.drop_table("personas")
    op.drop_index("ix_stocks_symbol", table_name="stocks")
    op.drop_table("stocks")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
