"""
yfinance fetcher service.

Pulls fundamentals from Yahoo Finance for NSE-listed stocks (suffix .NS).
Returns a normalized dict that matches our FundamentalSnapshot model.
"""
from __future__ import annotations

import logging
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)


def _safe_float(value: Any) -> float | None:
    """Convert to float if possible, else None. Handles yfinance's mixed-type returns."""
    if value is None:
        return None
    try:
        f = float(value)
        if f != f or f in (float("inf"), float("-inf")):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _pct(value: Any) -> float | None:
    """yfinance returns growth/margin/yield as decimals (0.15 = 15%). Convert to percent."""
    v = _safe_float(value)
    return v * 100 if v is not None else None


def fetch_fundamentals(ticker: str) -> dict[str, Any]:
    """
    Fetch fundamentals for a single ticker.

    Args:
        ticker: NSE ticker with .NS suffix (e.g., "RELIANCE.NS")

    Returns:
        dict with normalized fields matching our FundamentalSnapshot model,
        plus 'meta' (stock-level info) and 'raw' (full yfinance payload).

    Raises:
        ValueError: if ticker is invalid or no data found.
    """
    logger.info(f"Fetching fundamentals from yfinance for {ticker}")
    t = yf.Ticker(ticker)
    info = t.info

    if not info or not info.get("longName"):
        raise ValueError(f"No data found for ticker {ticker} on yfinance")

# 10-day average daily volume — quality of liquidity check
    avg_volume_10d: float | None = None
    try:
        hist = t.history(period="10d")
        if not hist.empty and "Volume" in hist.columns:
            avg_volume_10d = float(hist["Volume"].mean())
    except Exception as e:
        logger.warning(f"Failed to fetch 10d history for {ticker}: {e}")
    market_cap_raw = _safe_float(info.get("marketCap"))
    market_cap_cr = round(market_cap_raw / 1e7, 2) if market_cap_raw else None

    meta = {
        "ticker": ticker,
        "name": info.get("longName") or info.get("shortName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap_cr": market_cap_cr,
    }

    snapshot = {
        "pe_ratio": _safe_float(info.get("trailingPE")),
        "pb_ratio": _safe_float(info.get("priceToBook")),
        "roe_pct": _pct(info.get("returnOnEquity")),
        "debt_to_equity": _safe_float(info.get("debtToEquity")),
        "revenue_growth_yoy_pct": _pct(info.get("revenueGrowth")),
        "profit_margin_pct": _pct(info.get("profitMargins")),
        "eps": _safe_float(info.get("trailingEps")),
        "eps_growth_pct": _pct(info.get("earningsGrowth")),
        "dividend_yield_pct": _safe_float(info.get("dividendYield")),
        "working_capital_ratio": None,
        "quick_ratio": _safe_float(info.get("quickRatio")),
        "debtor_days": None,
        "public_holding_pct": None,
        "cash_flow_positive": None,
        "avg_volume_10d": avg_volume_10d,
        "source": "yfinance",
        "raw_data": {k: v for k, v in info.items() if isinstance(v, (str, int, float, bool, type(None)))},
    }

    # Normalize D/E heuristic — yfinance sometimes returns as percent (45 instead of 0.45)
    if snapshot["debt_to_equity"] is not None and snapshot["debt_to_equity"] > 10:
        snapshot["debt_to_equity"] = round(snapshot["debt_to_equity"] / 100, 2)

    return {"meta": meta, "snapshot": snapshot}