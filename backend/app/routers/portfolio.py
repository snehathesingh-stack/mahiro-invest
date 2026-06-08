from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Holding, Stock, User
from app.routers.stocks import persist_stock_data
from app.services.security import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class HoldingPayload(BaseModel):
    symbol: str
    quantity: float
    avg_buy_price: float


def _holding_dict(holding: Holding) -> dict:
    current = float(holding.stock.last_price or 0)
    qty = float(holding.quantity)
    avg = float(holding.avg_buy_price)
    invested = qty * avg
    value = qty * current
    created = holding.created_at.replace(tzinfo=timezone.utc) if holding.created_at and holding.created_at.tzinfo is None else holding.created_at
    days_held = max((datetime.now(timezone.utc) - created).days, 0) if created else 0
    return {
        "id": holding.id,
        "symbol": holding.stock.symbol,
        "company_name": holding.stock.company_name,
        "sector": holding.stock.sector,
        "quantity": qty,
        "avg_buy_price": avg,
        "current_price": current,
        "invested": invested,
        "current_value": value,
        "gain_loss": value - invested,
        "return_pct": ((value - invested) / invested * 100) if invested else 0,
        "days_held": days_held,
    }


@router.get("/")
def get_portfolio(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    holdings = db.query(Holding).filter(Holding.user_id == user.id).all()
    items = [_holding_dict(h) for h in holdings]
    invested = sum(i["invested"] for i in items)
    value = sum(i["current_value"] for i in items)
    sectors = {}
    for item in items:
        sectors[item["sector"] or "Unknown"] = sectors.get(item["sector"] or "Unknown", 0) + item["current_value"]
    return {
        "holdings": items,
        "stats": {"total_invested": invested, "current_value": value, "gain_loss": value - invested, "gain_loss_pct": ((value - invested) / invested * 100) if invested else 0},
        "sector_allocation": [{"sector": k, "value": v} for k, v in sectors.items()],
    }


@router.post("/")
def add_holding(payload: HoldingPayload, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    stock = db.query(Stock).filter(Stock.symbol == payload.symbol.upper()).first()
    if not stock:
        stock, _ = persist_stock_data(db, payload.symbol.upper())
    holding = Holding(user_id=user.id, stock_id=stock.id, quantity=payload.quantity, avg_buy_price=payload.avg_buy_price)
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return _holding_dict(holding)


@router.put("/{holding_id}")
def update_holding(holding_id: int, payload: HoldingPayload, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    holding = db.query(Holding).filter(Holding.id == holding_id, Holding.user_id == user.id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    stock = db.query(Stock).filter(Stock.symbol == payload.symbol.upper()).first()
    if not stock:
        stock, _ = persist_stock_data(db, payload.symbol.upper())
    holding.stock_id = stock.id
    holding.quantity = payload.quantity
    holding.avg_buy_price = payload.avg_buy_price
    db.commit()
    db.refresh(holding)
    return _holding_dict(holding)


@router.delete("/{holding_id}")
def delete_holding(holding_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    holding = db.query(Holding).filter(Holding.id == holding_id, Holding.user_id == user.id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    db.delete(holding)
    db.commit()
    return {"ok": True}
