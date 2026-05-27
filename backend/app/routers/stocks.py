"""
Stock endpoints — fetch fundamentals, list stocks, etc.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import yfinance_fetcher
from app.services.stock_service import upsert_stock, save_snapshot, get_latest_snapshot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


def _snapshot_to_dict(stock, snap) -> dict:
    """Serialize a (Stock, FundamentalSnapshot) pair for JSON response."""
    return {
        "ticker": stock.ticker,
        "name": stock.name,
        "sector": stock.sector,
        "industry": stock.industry,
        "market_cap_cr": float(stock.market_cap_cr) if stock.market_cap_cr else None,
        "fundamentals": {
            "pe_ratio": float(snap.pe_ratio) if snap.pe_ratio is not None else None,
            "pb_ratio": float(snap.pb_ratio) if snap.pb_ratio is not None else None,
            "roe_pct": float(snap.roe_pct) if snap.roe_pct is not None else None,
            "debt_to_equity": float(snap.debt_to_equity) if snap.debt_to_equity is not None else None,
            "revenue_growth_yoy_pct": float(snap.revenue_growth_yoy_pct) if snap.revenue_growth_yoy_pct is not None else None,
            "profit_margin_pct": float(snap.profit_margin_pct) if snap.profit_margin_pct is not None else None,
            "eps": float(snap.eps) if snap.eps is not None else None,
            "eps_growth_pct": float(snap.eps_growth_pct) if snap.eps_growth_pct is not None else None,
            "working_capital_ratio": float(snap.working_capital_ratio) if snap.working_capital_ratio is not None else None,
            "quick_ratio": float(snap.quick_ratio) if snap.quick_ratio is not None else None,
            "debtor_days": float(snap.debtor_days) if snap.debtor_days is not None else None,
            "public_holding_pct": float(snap.public_holding_pct) if snap.public_holding_pct is not None else None,
            "dividend_yield_pct": float(snap.dividend_yield_pct) if snap.dividend_yield_pct is not None else None,
            "cash_flow_positive": snap.cash_flow_positive,
        },
        "source": snap.source,
        "fetched_at": snap.fetched_at.isoformat() if snap.fetched_at else None,
    }


@router.post("/{ticker}/refresh")
def refresh_stock(ticker: str, db: Session = Depends(get_db)) -> dict:
    """
    Fetch fresh fundamentals from yfinance and persist a new snapshot.

    Example: POST /api/stocks/RELIANCE.NS/refresh
    """
    ticker = ticker.upper()
    try:
        data = yfinance_fetcher.fetch_fundamentals(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error fetching {ticker}")
        raise HTTPException(status_code=502, detail=f"Upstream error: {str(e)}")

    stock = upsert_stock(db, data["meta"])
    snap = save_snapshot(db, stock.id, data["snapshot"])
    db.commit()
    db.refresh(stock)
    db.refresh(snap)

    return _snapshot_to_dict(stock, snap)


@router.get("/{ticker}/fundamentals")
def get_stock_fundamentals(ticker: str, db: Session = Depends(get_db)) -> dict:
    """
    Get the latest cached fundamentals for a ticker.

    Example: GET /api/stocks/RELIANCE.NS/fundamentals
    """
    ticker = ticker.upper()
    result = get_latest_snapshot(db, ticker)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No fundamentals cached for {ticker}. Call POST /api/stocks/{ticker}/refresh first.",
        )
    stock, snap = result
    return _snapshot_to_dict(stock, snap)