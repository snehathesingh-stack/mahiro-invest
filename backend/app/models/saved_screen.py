from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class SavedScreen(Base):
    __tablename__ = "saved_screens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    persona_id = Column(Integer, ForeignKey("personas.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(200), nullable=False)
    symbols = Column(JSONB, nullable=False)
    criteria = Column(JSONB, nullable=False)
    results = Column(JSONB, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    persona = relationship("Persona")
