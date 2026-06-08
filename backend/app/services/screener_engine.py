from __future__ import annotations

from typing import Any


def _num(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _history(raw: dict, key: str) -> list[float]:
    return [float(v) for v in (raw or {}).get(key, []) if v is not None]


def _eval(name: str, passed: bool | None, value: Any, rule: str, reason: str | None = None) -> dict:
    if passed is None:
        return {"criterion": name, "status": "fail", "value": value, "rule": rule, "reason": reason or "Required data unavailable"}
    return {"criterion": name, "status": "pass" if passed else "fail", "value": value, "rule": rule, "reason": reason}


def evaluate_stock(stock, snapshot, criteria: dict) -> dict:
    filters = criteria.get("hard_filters", {}) if criteria else {}
    market_cap_rule = filters.get("market_cap_cr", {})
    pe_rule = filters.get("pe_ratio", {})
    eps_rule = filters.get("eps_trend", {})
    revenue_rule = filters.get("revenue_growth_yoy", {})
    margin_rule = filters.get("profit_margin", {})
    debt_rule = filters.get("debt_to_equity", {})
    roe_rule = filters.get("roe", {})
    cash_rule = filters.get("cash_flow_from_operations", {})
    debtor_rule = filters.get("debtor_days", {})
    holding_rule = filters.get("fii_dii_holding", {})
    ma_rule = filters.get("moving_average_signal", {})
    market_cap_min = _num(market_cap_rule.get("min")) or 5000
    pe_min = _num(pe_rule.get("min")) or 10
    pe_max = _num(pe_rule.get("max")) or 25
    pe_enabled = pe_rule.get("enabled", True)
    eps_lookback = int(eps_rule.get("lookback_years", 5))
    revenue_min = _num(revenue_rule.get("min")) or 10
    revenue_years = int(revenue_rule.get("sustained_years", 3))
    debt_max = _num(debt_rule.get("max")) or 1.0
    roe_min = _num(roe_rule.get("min")) or 15
    debtor_max = _num(debtor_rule.get("max")) or 100
    raw = snapshot.raw_json or {}
    market_cap_cr = stock.market_cap_cr
    pe = _num(snapshot.pe_ratio)
    eps_history = _history(raw, "eps_history")
    revenue_history = _history(raw, "revenue_growth_history")
    cfo_history = _history(raw, "cash_flow_history")
    fii_history = _history(raw, "fii_history")
    dii_history = _history(raw, "dii_history")
    evaluations = [
        _eval("Market Cap", market_cap_cr is not None and market_cap_cr > market_cap_min, market_cap_cr, f"> ₹{market_cap_min:,.0f} Cr"),
        _eval(
            "EPS Increasing",
            len(eps_history) >= eps_lookback and eps_history[-1] > eps_history[-eps_lookback],
            eps_history,
            f"{eps_lookback}-year upward trend",
        ),
        _eval(
            "Revenue Growth",
            len(revenue_history) >= revenue_years and all(v >= revenue_min for v in revenue_history[-revenue_years:]),
            revenue_history,
            f"≥ {revenue_min:g}% YoY for {revenue_years}+ years",
        ),
        _eval("Profit Margin", _num(snapshot.profit_margin) is not None and (not margin_rule.get("positive", True) or _num(snapshot.profit_margin) > 0), _num(snapshot.profit_margin), "positive"),
        _eval("Debt-to-Equity", _num(snapshot.debt_to_equity) is not None and _num(snapshot.debt_to_equity) < debt_max, _num(snapshot.debt_to_equity), f"< {debt_max:g}"),
        _eval("ROE", _num(snapshot.roe) is not None and _num(snapshot.roe) >= roe_min, _num(snapshot.roe), f"≥ {roe_min:g}%"),
        _eval(
            "Cash Flow from Operations",
            len(cfo_history) >= 2 and cfo_history[-1] > 0 and (not cash_rule.get("growing_yoy", True) or cfo_history[-1] >= cfo_history[0]),
            cfo_history,
            "positive and growing YoY",
        ),
        _eval("Debtor Days", _num(snapshot.debtor_days) is not None and _num(snapshot.debtor_days) < debtor_max, _num(snapshot.debtor_days), f"< {debtor_max:g} for all sectors"),
        _eval("FII Holding Trend", len(fii_history) >= 2 and (not holding_rule.get("both_increasing", True) or fii_history[-1] > fii_history[0]), fii_history, "increasing"),
        _eval("DII Holding Trend", len(dii_history) >= 2 and (not holding_rule.get("both_increasing", True) or dii_history[-1] > dii_history[0]), dii_history, "increasing"),
        _eval(
            "MA Signal",
            _num(snapshot.moving_avg_20d) is not None
            and _num(snapshot.moving_avg_200d) is not None
            and (not ma_rule.get("ma20_above_ma200", True) or _num(snapshot.moving_avg_20d) > _num(snapshot.moving_avg_200d)),
            {"ma20": _num(snapshot.moving_avg_20d), "ma200": _num(snapshot.moving_avg_200d)},
            "20DMA above 200DMA",
        ),
    ]
    if pe_enabled:
        evaluations.insert(1, _eval("P/E Ratio", pe is not None and pe_min <= pe <= pe_max, pe, f"{pe_min:g} to {pe_max:g}"))
    fail_count = sum(1 for item in evaluations if item["status"] == "fail")
    score = weighted_score(snapshot, raw, criteria)
    return {
        "evaluations": evaluations,
        "summary": {"pass": len(evaluations) - fail_count, "fail": fail_count, "verdict": "PASS" if fail_count == 0 else "FAIL"},
        "score": score if fail_count == 0 else 0,
    }


def weighted_score(snapshot, raw: dict, criteria: dict) -> float:
    weights = (criteria or {}).get("ranking_weights", {})
    revenue_weight = _num(weights.get("revenue_growth_yoy")) or 30
    margin_weight = _num(weights.get("profit_margin")) or 25
    eps_weight = _num(weights.get("eps_consistency")) or 25
    debt_weight = _num(weights.get("debt_to_equity")) or 20
    revenue = min(max((_num(snapshot.revenue_growth_yoy) or 0) / 25, 0), 1) * revenue_weight
    margin = min(max((_num(snapshot.profit_margin) or 0) / 30, 0), 1) * margin_weight
    eps_hist = _history(raw, "eps_history")
    eps_score = eps_weight if len(eps_hist) >= 5 and eps_hist[-1] > eps_hist[0] else 0
    debt = (1 - min(max((_num(snapshot.debt_to_equity) or 1), 0), 1)) * debt_weight
    return round(revenue + margin + eps_score + debt, 2)
