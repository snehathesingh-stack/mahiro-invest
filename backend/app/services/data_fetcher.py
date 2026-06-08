from __future__ import annotations

from datetime import date
from typing import Any

from app.services.defaults import sample_fundamentals


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_stock_data(symbol: str) -> dict:
    symbol = symbol.upper()
    fallback = sample_fundamentals(symbol)
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        hist = ticker.history(period="1y")
        fast = ticker.fast_info or {}
        close = hist["Close"] if not hist.empty and "Close" in hist else None
        price = _safe_float(getattr(fast, "last_price", None)) or fallback["last_price"]
        ma20 = _safe_float(close.tail(20).mean()) if close is not None else fallback["snapshot"]["moving_avg_20d"]
        ma200 = _safe_float(close.tail(200).mean()) if close is not None else fallback["snapshot"]["moving_avg_200d"]
        market_cap = _safe_float(info.get("marketCap"))
        snapshot = fallback["snapshot"].copy()
        snapshot.update(
            {
                "pe_ratio": _safe_float(info.get("trailingPE")) or snapshot["pe_ratio"],
                "eps": _safe_float(info.get("trailingEps")) or snapshot["eps"],
                "roe": ((_safe_float(info.get("returnOnEquity")) or 0) * 100) or snapshot["roe"],
                "debt_to_equity": (_safe_float(info.get("debtToEquity")) or snapshot["debt_to_equity"] * 100) / 100,
                "profit_margin": ((_safe_float(info.get("profitMargins")) or 0) * 100) or snapshot["profit_margin"],
                "dividend_yield": ((_safe_float(info.get("dividendYield")) or 0) * 100) or snapshot["dividend_yield"],
                "moving_avg_20d": round(ma20, 2),
                "moving_avg_200d": round(ma200, 2),
                "raw_json": {**snapshot["raw_json"], "yfinance_info": info, "source_date": date.today().isoformat()},
            }
        )
        return {
            "symbol": symbol,
            "company_name": info.get("longName") or info.get("shortName") or fallback["company_name"],
            "sector": info.get("sector") or fallback["sector"],
            "market_cap_cr": (market_cap / 10_000_000) if market_cap else fallback["market_cap_cr"],
            "last_price": price,
            "snapshot": snapshot,
        }
    except Exception:
        return fallback


def upcoming_earnings(days: int = 90) -> list[dict]:
    from app.services.defaults import sample_earnings

    return [item for item in sample_earnings(days) if item["earnings_date"]]
