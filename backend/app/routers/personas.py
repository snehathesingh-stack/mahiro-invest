"""
Persona endpoints — manage investor personas (rule sets that define screening criteria).
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Persona

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personas", tags=["personas"])


def _persona_to_dict(p: Persona) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "owner": p.owner,
        "style": p.style,
        "config": p.config,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


@router.get("")
def list_personas(owner: str | None = None, db: Session = Depends(get_db)) -> list[dict]:
    """List all personas, optionally filtered by owner."""
    q = db.query(Persona)
    if owner:
        q = q.filter(Persona.owner == owner)
    return [_persona_to_dict(p) for p in q.all()]


@router.get("/{persona_id}")
def get_persona(persona_id: int, db: Session = Depends(get_db)) -> dict:
    """Get one persona by id."""
    p = db.query(Persona).filter(Persona.id == persona_id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    return _persona_to_dict(p)