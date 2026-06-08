from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Holding, User, Watchlist
from app.routers.stocks import persist_stock_data
from app.services.data_fetcher import upcoming_earnings
from app.services.security import get_current_user

router = APIRouter(prefix="/earnings", tags=["earnings"])


@router.get("/upcoming")
def upcoming(days: int = Query(30, ge=30, le=90), scope: str = "full", watchlist_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    items = upcoming_earnings(days)
    allowed = None
    if scope == "portfolio":
        allowed = {h.stock.symbol for h in db.query(Holding).filter(Holding.user_id == user.id).all()}
    elif scope == "watchlist" and watchlist_id:
        w = db.query(Watchlist).filter(Watchlist.id == watchlist_id, Watchlist.user_id == user.id).first()
        allowed = set(w.stock_ids if w else [])
    if allowed is not None:
        items = [item for item in items if item["symbol"] in allowed]
    return items


@router.get("/rerun/{symbol}")
def rerun(symbol: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    stock, snap = persist_stock_data(db, symbol.upper())
    return {"symbol": stock.symbol, "message": "Post-earnings persona re-evaluation data refreshed.", "snapshot_id": snap.id}
