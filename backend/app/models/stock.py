from sqlalchemy import Column, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import relationship
from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(200), nullable=False)
    sector = Column(String(100))
    market_cap = Column(Numeric(20, 2))
    last_price = Column(Numeric(15, 2))
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    snapshots = relationship("FundamentalSnapshot", back_populates="stock", cascade="all, delete-orphan")
    holdings = relationship("Holding", back_populates="stock", cascade="all, delete-orphan")

    @property
    def ticker(self) -> str:
        return self.symbol

    @property
    def name(self) -> str:
        return self.company_name

    @property
    def market_cap_cr(self) -> float | None:
        if self.market_cap is None:
            return None
        return float(self.market_cap) / 10_000_000
