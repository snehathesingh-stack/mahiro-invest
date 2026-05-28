"""
Persona evaluator — given fundamentals and a persona, returns pass/fail per criterion.

Returns a list of evaluations, one per filter the persona defines. Each evaluation
includes the criterion name, the actual value, the threshold, and whether it passed.

Criteria we can't evaluate yet (e.g., sustained_years for revenue growth, EPS trend
over multiple years, moving averages) are marked status='skipped' with a reason.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)


def _to_float(value: Any) -> float | None:
    """Coerce Decimal/int/str to float safely. Returns None if not coercible."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _eval_min(value: Any, threshold: float, label: str) -> dict:
    v = _to_float(value)
    if v is None:
        return {"criterion": label, "status": "skipped", "reason": "data missing"}
    passed = v >= threshold
    return {
        "criterion": label,
        "status": "pass" if passed else "fail",
        "value": v,
        "rule": f"≥ {threshold}",
    }


def _eval_max(value: Any, threshold: float, label: str) -> dict:
    v = _to_float(value)
    if v is None:
        return {"criterion": label, "status": "skipped", "reason": "data missing"}
    passed = v <= threshold
    return {
        "criterion": label,
        "status": "pass" if passed else "fail",
        "value": v,
        "rule": f"≤ {threshold}",
    }


def _eval_range(value: Any, low: float, high: float, label: str) -> dict:
    v = _to_float(value)
    if v is None:
        return {"criterion": label, "status": "skipped", "reason": "data missing"}
    passed = low <= v <= high
    return {
        "criterion": label,
        "status": "pass" if passed else "fail",
        "value": v,
        "rule": f"{low}–{high}",
    }


def evaluate(fundamentals: dict[str, Any], persona_config: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate one stock's fundamentals against a persona's hard filters.

    Args:
        fundamentals: the 'fundamentals' dict from a snapshot (pe_ratio, roe_pct, etc.)
        persona_config: the persona's full config JSON (hard_filters, ranking_weights, etc.)

    Returns:
        {
            "evaluations": [{"criterion": ..., "status": "pass|fail|skipped", ...}, ...],
            "summary": {"pass": N, "fail": M, "skipped": K, "verdict": "PASS|FAIL"},
        }
    """
    filters = persona_config.get("hard_filters", {})
    evaluations: list[dict] = []

    # Market cap (min)
    if "market_cap_cr" in filters:
        evaluations.append(
            _eval_min(
                fundamentals.get("market_cap_cr"),
                filters["market_cap_cr"]["min"],
                "Market Cap (₹ Cr)",
            )
        )

    # P/E (range)
    if "pe_ratio" in filters:
        r = filters["pe_ratio"]
        evaluations.append(_eval_range(fundamentals.get("pe_ratio"), r["min"], r["max"], "P/E Ratio"))

    # Revenue growth (min)
    if "revenue_growth_yoy_pct" in filters:
        evaluations.append(
            _eval_min(
                fundamentals.get("revenue_growth_yoy_pct"),
                filters["revenue_growth_yoy_pct"]["min"],
                "Revenue Growth YoY (%)",
            )
        )

    # Profit margin (min)
    if "profit_margin_pct" in filters:
        evaluations.append(
            _eval_min(
                fundamentals.get("profit_margin_pct"),
                filters["profit_margin_pct"]["min"],
                "Profit Margin (%)",
            )
        )

    # EPS trend — needs multi-year, skip for now
    if "eps_trend" in filters:
        evaluations.append(
            {
                "criterion": "EPS Increasing YoY",
                "status": "skipped",
                "reason": "needs multi-year history (Week 2)",
            }
        )

    # Working capital ratio (min)
    if "working_capital_ratio" in filters:
        evaluations.append(
            _eval_min(
                fundamentals.get("working_capital_ratio"),
                filters["working_capital_ratio"]["min"],
                "Working Capital Ratio",
            )
        )

    # Quick ratio (min)
    if "quick_ratio" in filters:
        evaluations.append(
            _eval_min(
                fundamentals.get("quick_ratio"),
                filters["quick_ratio"]["min"],
                "Quick Ratio",
            )
        )

    # Debt to equity (max)
    if "debt_to_equity" in filters:
        evaluations.append(
            _eval_max(
                fundamentals.get("debt_to_equity"),
                filters["debt_to_equity"]["max"],
                "Debt to Equity",
            )
        )

    # P/B (max)
    if "pb_ratio" in filters:
        evaluations.append(
            _eval_max(
                fundamentals.get("pb_ratio"),
                filters["pb_ratio"]["max"],
                "P/B Ratio",
            )
        )

    # Debtor days (max)
    if "debtor_days" in filters:
        evaluations.append(
            _eval_max(
                fundamentals.get("debtor_days"),
                filters["debtor_days"]["max"],
                "Debtor Days",
            )
        )

    # Public holding (max)
    if "public_holding_pct" in filters:
        evaluations.append(
            _eval_max(
                fundamentals.get("public_holding_pct"),
                filters["public_holding_pct"]["max"],
                "Public Holding (%)",
            )
        )

    # Cash flow
    if "cash_flow" in filters:
        cf = fundamentals.get("cash_flow_positive")
        if cf is None:
            evaluations.append(
                {
                    "criterion": "Cash Flow Positive & Growing",
                    "status": "skipped",
                    "reason": "data missing",
                }
            )
        else:
            evaluations.append(
                {
                    "criterion": "Cash Flow Positive & Growing",
                    "status": "pass" if cf else "fail",
                    "value": cf,
                    "rule": "positive + growing YoY",
                }
            )

    # FII+DII trend — needs history
    if "fii_dii_holding" in filters:
        evaluations.append(
            {
                "criterion": "FII+DII Holding Trend",
                "status": "skipped",
                "reason": "needs multi-quarter history (Week 2)",
            }
        )

    # Moving average signal — needs price history
    if "moving_average_signal" in filters:
        evaluations.append(
            {
                "criterion": "20DMA Golden Cross",
                "status": "skipped",
                "reason": "needs price history (Week 2)",
            }
        )

    # ROE (min)
    if "roe_pct" in filters:
        evaluations.append(
            _eval_min(
                fundamentals.get("roe_pct"),
                filters["roe_pct"]["min"],
                "Return on Equity (%)",
            )
        )
   # Avg volume 10-day (min) — liquidity filter
    if "avg_volume_10d" in filters:
        evaluations.append(
            _eval_min(
                fundamentals.get("avg_volume_10d"),
                filters["avg_volume_10d"]["min"],
                "Avg Daily Volume (10d)",
            )
        )
    # Summary
    pass_count = sum(1 for e in evaluations if e["status"] == "pass")
    fail_count = sum(1 for e in evaluations if e["status"] == "fail")
    skip_count = sum(1 for e in evaluations if e["status"] == "skipped")
    verdict = "PASS" if fail_count == 0 else "FAIL"

    return {
        "evaluations": evaluations,
        "summary": {
            "pass": pass_count,
            "fail": fail_count,
            "skipped": skip_count,
            "verdict": verdict,
        },
    }