"""
Merger service — combines yfinance + screener.in fundamentals into one snapshot.

Each field has a preferred source. If the preferred source returns None, we fall back
to the other. The result is a single 'merged' snapshot with source='merged'.

Why this layer exists: yfinance gives clean basics (price, market cap, sector) but
misses Indian-specific fields like debtor days and public holding. screener.in
provides those but has flakier number coverage. Together they form a complete picture.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


# Per-field source preference. First source listed is preferred; if None, fall back to second.
# If a field isn't in this map, it's taken from yfinance by default.
FIELD_PREFERENCE = {
    # Stock metadata
    "ticker": ["yfinance", "screener"],
    "name": ["yfinance", "screener"],
    "sector": ["yfinance", "screener"],
    "industry": ["yfinance", "screener"],
    "market_cap_cr": ["yfinance", "screener"],

    # Valuation
    "pe_ratio": ["screener", "yfinance"],
    "pb_ratio": ["screener", "yfinance"],

    # Profitability
    "roe_pct": ["screener", "yfinance"],
    "profit_margin_pct": ["yfinance", "screener"],
    "eps": ["yfinance", "screener"],
    "eps_growth_pct": ["yfinance", "screener"],
    "revenue_growth_yoy_pct": ["yfinance", "screener"],

    # Leverage & liquidity
    "debt_to_equity": ["yfinance", "screener"],
    "quick_ratio": ["yfinance", "screener"],
    "working_capital_ratio": ["yfinance", "screener"],

    # Indian-specific (screener-only fields)
    "debtor_days": ["screener", "yfinance"],
    "public_holding_pct": ["screener", "yfinance"],

    # Income
    "dividend_yield_pct": ["screener", "yfinance"],
    "cash_flow_positive": ["yfinance", "screener"],
    # Liquidity
    "avg_volume_10d": ["yfinance", "screener"],
}


def _pick(value_from_source: dict[str, Optional[Any]], preference: list[str]) -> Optional[Any]:
    """
    Given a {source_name: value} dict and a preference order, return the first non-None value.
    """
    for source in preference:
        v = value_from_source.get(source)
        if v is not None:
            return v
    return None


def merge_fundamentals(
    yfinance_result: Optional[dict[str, Any]],
    screener_result: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """
    Merge two source results into one canonical snapshot.

    Either input can be None (e.g., if that source failed). At least one must be
    non-None — caller's responsibility.
    """
    if yfinance_result is None and screener_result is None:
        raise ValueError("merge_fundamentals: both sources are None")

    yf_meta = (yfinance_result or {}).get("meta", {})
    yf_snap = (yfinance_result or {}).get("snapshot", {})
    sc_meta = (screener_result or {}).get("meta", {})
    sc_snap = (screener_result or {}).get("snapshot", {})

    # Build merged meta
    merged_meta = {}
    for field in ["ticker", "name", "sector", "industry", "market_cap_cr"]:
        merged_meta[field] = _pick(
            {"yfinance": yf_meta.get(field), "screener": sc_meta.get(field)},
            FIELD_PREFERENCE.get(field, ["yfinance", "screener"]),
        )

    # Build merged snapshot
    merged_snap: dict[str, Any] = {}
    snapshot_fields = [
        "pe_ratio", "pb_ratio", "roe_pct", "debt_to_equity",
        "revenue_growth_yoy_pct", "profit_margin_pct",
        "eps", "eps_growth_pct",
        "working_capital_ratio", "quick_ratio",
        "debtor_days", "public_holding_pct",
        "dividend_yield_pct", "cash_flow_positive","avg_volume_10d",
    ]
    for field in snapshot_fields:
        merged_snap[field] = _pick(
            {"yfinance": yf_snap.get(field), "screener": sc_snap.get(field)},
            FIELD_PREFERENCE.get(field, ["yfinance", "screener"]),
        )

    merged_snap["source"] = "merged"

    # Keep both raw payloads for audit trail — debugging gold later
    merged_snap["raw_data"] = {
        "yfinance": yf_snap.get("raw_data") if yfinance_result else None,
        "screener": sc_snap.get("raw_data") if screener_result else None,
    }

    # Audit: which source won each field
    provenance: dict[str, str] = {}
    for field in snapshot_fields:
        for source in FIELD_PREFERENCE.get(field, ["yfinance", "screener"]):
            value = (yf_snap if source == "yfinance" else sc_snap).get(field)
            if value is not None:
                provenance[field] = source
                break
        else:
            provenance[field] = "none"
    merged_snap["raw_data"]["provenance"] = provenance

    logger.info(f"Merged fundamentals for {merged_meta.get('ticker')}: {provenance}")

    return {"meta": merged_meta, "snapshot": merged_snap}