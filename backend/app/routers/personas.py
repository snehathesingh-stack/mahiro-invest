from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Persona, User
from app.serializers import persona_dict
from app.services.defaults import persona_preset
from app.services.security import get_current_user

router = APIRouter(prefix="/personas", tags=["personas"])


class PersonaPayload(BaseModel):
    name: str
    description: str | None = None
    criteria: dict


class PresetPayload(BaseModel):
    name: str


@router.get("/")
def list_personas(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    return [persona_dict(p) for p in db.query(Persona).filter(Persona.user_id == user.id).all()]


@router.get("/{persona_id}")
def get_persona(persona_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    p = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    return persona_dict(p)


@router.post("/")
def create_persona(payload: PersonaPayload, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    persona = Persona(user_id=user.id, name=payload.name, description=payload.description, criteria=payload.criteria)
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona_dict(persona)


@router.post("/preset")
def create_preset_persona(payload: PresetPayload, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    name, description, criteria = persona_preset(payload.name)
    persona = Persona(user_id=user.id, name=name, description=description, criteria=criteria)
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona_dict(persona)


@router.post("/{persona_id}/duplicate")
def duplicate_persona(persona_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    source = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Persona not found")
    persona = Persona(
        user_id=user.id,
        name=f"{source.name} copy",
        description=source.description,
        criteria=source.criteria,
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona_dict(persona)


@router.put("/{persona_id}")
def update_persona(persona_id: int, payload: PersonaPayload, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    persona = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    persona.name = payload.name
    persona.description = payload.description
    persona.criteria = payload.criteria
    db.commit()
    db.refresh(persona)
    return persona_dict(persona)


@router.delete("/{persona_id}")
def delete_persona(persona_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    persona = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    db.delete(persona)
    db.commit()
    return {"ok": True}
