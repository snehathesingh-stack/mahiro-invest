from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FundamentalSnapshot, Persona, Stock, User
from app.routers.stocks import persist_stock_data
from app.serializers import snapshot_dict, stock_dict
from app.services.llm_explainer import explain
from app.services.screener_engine import evaluate_stock
from app.services.security import get_current_user

router = APIRouter(prefix="/screener", tags=["screener"])


class ScreenerRun(BaseModel):
    persona_id: int
    symbols: list[str] | None = None


def _latest(db: Session, stock_id: int):
    return db.query(FundamentalSnapshot).filter(FundamentalSnapshot.stock_id == stock_id).order_by(FundamentalSnapshot.fetched_at.desc()).first()


@router.post("/run")
def run_screener(payload: ScreenerRun, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    persona = db.query(Persona).filter(Persona.id == payload.persona_id, Persona.user_id == user.id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    stocks = db.query(Stock).all()
    if payload.symbols:
        wanted = {s.upper() for s in payload.symbols}
        stocks = [s for s in stocks if s.symbol in wanted]
    results = []
    for stock in stocks:
        snap = _latest(db, stock.id)
        if not snap:
            stock, snap = persist_stock_data(db, stock.symbol)
        evaluation = evaluate_stock(stock, snap, persona.criteria)
        results.append({**stock_dict(stock), "fundamentals": snapshot_dict(snap), **evaluation})
    results.sort(key=lambda r: (r["summary"]["verdict"] != "PASS", -r["score"], r["symbol"]))
    return {"persona": {"id": persona.id, "name": persona.name}, "results": results}


@router.get("/explain/{symbol}/{persona_id}")
def explain_stock(symbol: str, persona_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    persona = db.query(Persona).filter(Persona.id == persona_id, Persona.user_id == user.id).first()
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    if not persona or not stock:
        raise HTTPException(status_code=404, detail="Persona or stock not found")
    snap = _latest(db, stock.id)
    if not snap:
        stock, snap = persist_stock_data(db, stock.symbol)
    evaluation = evaluate_stock(stock, snap, persona.criteria)
    return {"symbol": stock.symbol, "persona_id": persona.id, "explanation": explain(stock.symbol, persona.name, evaluation)}
