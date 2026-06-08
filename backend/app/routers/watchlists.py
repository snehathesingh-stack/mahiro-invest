from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Watchlist
from app.services.security import get_current_user

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


class WatchlistPayload(BaseModel):
    name: str
    stock_ids: list[str] = []


def _dict(w: Watchlist) -> dict:
    return {"id": w.id, "name": w.name, "stock_ids": w.stock_ids, "created_at": w.created_at.isoformat() if w.created_at else None}


@router.get("/")
def list_watchlists(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    return [_dict(w) for w in db.query(Watchlist).filter(Watchlist.user_id == user.id).all()]


@router.post("/")
def create_watchlist(payload: WatchlistPayload, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    w = Watchlist(user_id=user.id, name=payload.name, stock_ids=[s.upper() for s in payload.stock_ids])
    db.add(w)
    db.commit()
    db.refresh(w)
    return _dict(w)


@router.put("/{watchlist_id}")
def update_watchlist(watchlist_id: int, payload: WatchlistPayload, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    w = db.query(Watchlist).filter(Watchlist.id == watchlist_id, Watchlist.user_id == user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    w.name = payload.name
    w.stock_ids = [s.upper() for s in payload.stock_ids]
    db.commit()
    db.refresh(w)
    return _dict(w)


@router.delete("/{watchlist_id}")
def delete_watchlist(watchlist_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    w = db.query(Watchlist).filter(Watchlist.id == watchlist_id, Watchlist.user_id == user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    db.delete(w)
    db.commit()
    return {"ok": True}
