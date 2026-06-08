from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FundamentalSnapshot, Stock
from app.serializers import snapshot_dict, stock_dict
from app.services.data_fetcher import fetch_stock_data

router = APIRouter(prefix="/stocks", tags=["stocks"])


def latest_snapshot(db: Session, stock_id: int):
    return db.query(FundamentalSnapshot).filter(FundamentalSnapshot.stock_id == stock_id).order_by(FundamentalSnapshot.fetched_at.desc()).first()


def persist_stock_data(db: Session, symbol: str):
    data = fetch_stock_data(symbol)
    stock = db.query(Stock).filter(Stock.symbol == data["symbol"]).first()
    if not stock:
        stock = Stock(symbol=data["symbol"], company_name=data["company_name"], sector=data["sector"])
        db.add(stock)
        db.flush()
    stock.company_name = data["company_name"]
    stock.sector = data["sector"]
    stock.market_cap = data["market_cap_cr"] * 10_000_000
    stock.last_price = data["last_price"]
    snap = FundamentalSnapshot(stock_id=stock.id, source="yfinance", **data["snapshot"])
    db.add(snap)
    db.commit()
    db.refresh(stock)
    db.refresh(snap)
    return stock, snap


@router.get("/")
def list_stocks(db: Session = Depends(get_db)) -> list[dict]:
    return [stock_dict(s, latest_snapshot(db, s.id)) for s in db.query(Stock).order_by(Stock.symbol).all()]


@router.get("/{symbol}")
def get_stock(symbol: str, db: Session = Depends(get_db)) -> dict:
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock_dict(stock, latest_snapshot(db, stock.id))


@router.post("/refresh/{symbol}")
def refresh_stock(symbol: str, db: Session = Depends(get_db)) -> dict:
    stock, snap = persist_stock_data(db, symbol.upper())
    return stock_dict(stock, snap)
