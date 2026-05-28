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
            "avg_volume_10d": float(snap.avg_volume_10d) if snap.avg_volume_10d is not None else None,
        },
        "source": snap.source,
        "fetched_at": snap.fetched_at.isoformat() if snap.fetched_at else None,
    }


@router.post("/{ticker}/refresh")
def refresh_stock(
    ticker: str,
    source: str = "merged",
    db: Session = Depends(get_db),
) -> dict:
    """
    Fetch fresh fundamentals and persist a new snapshot.

    Query params:
        source: "yfinance" | "screener" | "merged" (default: merged)

    Example: POST /api/stocks/RELIANCE.NS/refresh
             POST /api/stocks/RELIANCE.NS/refresh?source=screener
    """
    from app.services import yfinance_fetcher, screener_fetcher, merger

    ticker = ticker.upper()
    source = source.lower()

    if source not in ("yfinance", "screener", "merged"):
        raise HTTPException(status_code=400, detail=f"Invalid source: {source}")

    yf_result = None
    sc_result = None
    errors: dict[str, str] = {}

    # Fetch from yfinance if needed
    if source in ("yfinance", "merged"):
        try:
            yf_result = yfinance_fetcher.fetch_fundamentals(ticker)
        except Exception as e:
            errors["yfinance"] = str(e)
            logger.warning(f"yfinance failed for {ticker}: {e}")

    # Fetch from screener if needed
    if source in ("screener", "merged"):
        try:
            sc_result = screener_fetcher.fetch_fundamentals(ticker)
        except Exception as e:
            errors["screener"] = str(e)
            logger.warning(f"screener failed for {ticker}: {e}")

    # Decide what to do based on what succeeded
    if source == "yfinance":
        if yf_result is None:
            raise HTTPException(
                status_code=502,
                detail=f"yfinance failed: {errors.get('yfinance', 'unknown')}",
            )
        data = yf_result
    elif source == "screener":
        if sc_result is None:
            raise HTTPException(
                status_code=502,
                detail=f"screener failed: {errors.get('screener', 'unknown')}",
            )
        data = sc_result
    else:  # merged
        if yf_result is None and sc_result is None:
            raise HTTPException(
                status_code=502,
                detail=f"All sources failed. yfinance: {errors.get('yfinance')}; screener: {errors.get('screener')}",
            )
        data = merger.merge_fundamentals(yf_result, sc_result)

    stock = upsert_stock(db, data["meta"])
    snap = save_snapshot(db, stock.id, data["snapshot"])
    db.commit()
    db.refresh(stock)
    db.refresh(snap)

    response = _snapshot_to_dict(stock, snap)
    if errors:
        response["partial_errors"] = errors
    return response

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
@router.get("/{ticker}/evaluate")
def evaluate_stock(
    ticker: str,
    persona_id: int = 1,
    db: Session = Depends(get_db),
) -> dict:
    """
    Evaluate the latest snapshot of a stock against a persona's criteria.

    Example: GET /api/stocks/RELIANCE.NS/evaluate?persona_id=1
    """
    from app.services import persona_evaluator
    from app.models import Persona

    ticker = ticker.upper()
    result = get_latest_snapshot(db, ticker)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot for {ticker}. Call POST /api/stocks/{ticker}/refresh first.",
        )

    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")

    stock, snap = result
    snapshot_dict = _snapshot_to_dict(stock, snap)

    fundamentals_with_mcap = {
        **snapshot_dict["fundamentals"],
        "market_cap_cr": snapshot_dict["market_cap_cr"],
    }
    evaluation = persona_evaluator.evaluate(fundamentals_with_mcap, persona.config)

    return {
        "ticker": stock.ticker,
        "name": stock.name,
        "persona": {"id": persona.id, "name": persona.name},
        "fundamentals": snapshot_dict["fundamentals"],
        "market_cap_cr": snapshot_dict["market_cap_cr"],
        "sector": snapshot_dict["sector"],
        "industry": snapshot_dict["industry"],
        **evaluation,
        "source": snapshot_dict["source"],
        "fetched_at": snapshot_dict["fetched_at"],
    }