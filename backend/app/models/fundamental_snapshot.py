from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class FundamentalSnapshot(Base):
    __tablename__ = "fundamental_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True)

    pe_ratio = Column(Numeric(10, 2))
    pb_ratio = Column(Numeric(10, 2))
    roe_pct = Column(Numeric(10, 2))
    debt_to_equity = Column(Numeric(10, 2))
    revenue_growth_yoy_pct = Column(Numeric(10, 2))
    profit_margin_pct = Column(Numeric(10, 2))
    eps = Column(Numeric(10, 2))
    eps_growth_pct = Column(Numeric(10, 2))
    working_capital_ratio = Column(Numeric(10, 2))
    quick_ratio = Column(Numeric(10, 2))
    debtor_days = Column(Numeric(10, 2))
    public_holding_pct = Column(Numeric(10, 2))
    dividend_yield_pct = Column(Numeric(10, 2))
    cash_flow_positive = Column(Boolean)

    source = Column(String(50), nullable=False)  # "yfinance" / "screener" / "merged"
    raw_data = Column(JSONB)

    fetched_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    stock = relationship("Stock", back_populates="snapshots")