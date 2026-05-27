from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200))
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap_cr = Column(Numeric(15, 2))  # market cap in crores

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    snapshots = relationship("FundamentalSnapshot", back_populates="stock", cascade="all, delete-orphan")
    holdings = relationship("Holding", back_populates="stock", cascade="all, delete-orphan")