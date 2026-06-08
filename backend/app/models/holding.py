from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import relationship
from app.database import Base


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Numeric(15, 4), nullable=False)
    avg_buy_price = Column(Numeric(15, 2), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="holdings")
    stock = relationship("Stock", back_populates="holdings")
