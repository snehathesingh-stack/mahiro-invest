from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class FundamentalSnapshot(Base):
    __tablename__ = "fundamental_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_date = Column(Date, server_default=func.current_date(), nullable=False, index=True)
    pe_ratio = Column(Numeric(10, 2))
    eps = Column(Numeric(10, 2))
    roe = Column(Numeric(10, 2))
    debt_to_equity = Column(Numeric(10, 2))
    revenue_growth_yoy = Column(Numeric(10, 2))
    profit_margin = Column(Numeric(10, 2))
    cash_flow_from_operations = Column(Numeric(20, 2))
    cash_flow_positive = Column(Boolean)
    debtor_days = Column(Numeric(10, 2))
    fii_holding_pct = Column(Numeric(10, 2))
    dii_holding_pct = Column(Numeric(10, 2))
    moving_avg_20d = Column(Numeric(15, 2))
    moving_avg_200d = Column(Numeric(15, 2))
    dividend_yield = Column(Numeric(10, 2))
    raw_json = Column(JSONB)
    source = Column(String(50), nullable=False, default="yfinance")
    fetched_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    stock = relationship("Stock", back_populates="snapshots")

    @property
    def roe_pct(self):
        return self.roe

    @property
    def revenue_growth_yoy_pct(self):
        return self.revenue_growth_yoy

    @property
    def profit_margin_pct(self):
        return self.profit_margin

    @property
    def dividend_yield_pct(self):
        return self.dividend_yield
