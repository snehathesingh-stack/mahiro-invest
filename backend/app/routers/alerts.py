from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Persona, User
from app.services.alert_engine import active_alerts
from app.services.security import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/")
def alerts(persona_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    q = db.query(Persona).filter(Persona.user_id == user.id)
    persona = q.filter(Persona.id == persona_id).first() if persona_id else q.first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return active_alerts(db, user, persona)
