"""
Stock service — handles DB operations for stocks and their fundamental snapshots.
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models import Stock, FundamentalSnapshot

logger = logging.getLogger(__name__)


def upsert_stock(db: Session, meta: dict[str, Any]) -> Stock:
    """
    Insert or update a stock record based on ticker. Returns the persisted Stock row.
    """
    ticker = meta["ticker"]
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()

    if stock is None:
        stock = Stock(
            ticker=ticker,
            name=meta.get("name"),
            sector=meta.get("sector"),
            industry=meta.get("industry"),
            market_cap_cr=meta.get("market_cap_cr"),
        )
        db.add(stock)
        logger.info(f"Created new stock: {ticker}")
    else:
        stock.name = meta.get("name") or stock.name
        stock.sector = meta.get("sector") or stock.sector
        stock.industry = meta.get("industry") or stock.industry
        stock.market_cap_cr = meta.get("market_cap_cr") or stock.market_cap_cr
        logger.info(f"Updated existing stock: {ticker}")

    db.flush()
    return stock


def save_snapshot(db: Session, stock_id: int, snapshot_data: dict[str, Any]) -> FundamentalSnapshot:
    """
    Persist a new FundamentalSnapshot row.
    """
    snap = FundamentalSnapshot(
        stock_id=stock_id,
        pe_ratio=snapshot_data.get("pe_ratio"),
        pb_ratio=snapshot_data.get("pb_ratio"),
        roe_pct=snapshot_data.get("roe_pct"),
        debt_to_equity=snapshot_data.get("debt_to_equity"),
        revenue_growth_yoy_pct=snapshot_data.get("revenue_growth_yoy_pct"),
        profit_margin_pct=snapshot_data.get("profit_margin_pct"),
        eps=snapshot_data.get("eps"),
        eps_growth_pct=snapshot_data.get("eps_growth_pct"),
        working_capital_ratio=snapshot_data.get("working_capital_ratio"),
        quick_ratio=snapshot_data.get("quick_ratio"),
        debtor_days=snapshot_data.get("debtor_days"),
        public_holding_pct=snapshot_data.get("public_holding_pct"),
        dividend_yield_pct=snapshot_data.get("dividend_yield_pct"),
        cash_flow_positive=snapshot_data.get("cash_flow_positive"),
        source=snapshot_data["source"],
        raw_data=snapshot_data.get("raw_data"),
    )
    db.add(snap)
    db.flush()
    return snap


def get_latest_snapshot(db: Session, ticker: str) -> tuple[Stock, FundamentalSnapshot] | None:
    """
    Get the most recent snapshot for a ticker.
    """
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        return None
    snap = (
        db.query(FundamentalSnapshot)
        .filter(FundamentalSnapshot.stock_id == stock.id)
        .order_by(FundamentalSnapshot.fetched_at.desc())
        .first()
    )
    if not snap:
        return None
    return stock, snap