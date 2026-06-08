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
    raw = snapshot.raw_json or {}
    market_cap_cr = stock.market_cap_cr
    pe = _num(snapshot.pe_ratio)
    eps_history = _history(raw, "eps_history")
    revenue_history = _history(raw, "revenue_growth_history")
    cfo_history = _history(raw, "cash_flow_history")
    fii_history = _history(raw, "fii_history")
    dii_history = _history(raw, "dii_history")
    evaluations = [
        _eval("Market Cap", market_cap_cr is not None and market_cap_cr > 5000, market_cap_cr, "> ₹5,000 Cr"),
        _eval("P/E Ratio", pe is not None and 10 <= pe <= 25, pe, "10 to 25"),
        _eval("EPS Increasing", len(eps_history) >= 5 and eps_history[-1] > eps_history[0], eps_history, "5-year upward trend"),
        _eval("Revenue Growth", len(revenue_history) >= 3 and all(v >= 10 for v in revenue_history[-3:]), revenue_history, "≥ 10% YoY for 3+ years"),
        _eval("Profit Margin", _num(snapshot.profit_margin) is not None and _num(snapshot.profit_margin) > 0, _num(snapshot.profit_margin), "positive"),
        _eval("Debt-to-Equity", _num(snapshot.debt_to_equity) is not None and _num(snapshot.debt_to_equity) < 1.0, _num(snapshot.debt_to_equity), "< 1.0"),
        _eval("ROE", _num(snapshot.roe) is not None and _num(snapshot.roe) >= 15, _num(snapshot.roe), "≥ 15%"),
        _eval("Cash Flow from Operations", len(cfo_history) >= 2 and cfo_history[-1] > 0 and cfo_history[-1] >= cfo_history[0], cfo_history, "positive and growing YoY"),
        _eval("Debtor Days", _num(snapshot.debtor_days) is not None and _num(snapshot.debtor_days) < 100, _num(snapshot.debtor_days), "< 100 for all sectors"),
        _eval("FII Holding Trend", len(fii_history) >= 2 and fii_history[-1] > fii_history[0], fii_history, "increasing"),
        _eval("DII Holding Trend", len(dii_history) >= 2 and dii_history[-1] > dii_history[0], dii_history, "increasing"),
        _eval("MA Signal", _num(snapshot.moving_avg_20d) is not None and _num(snapshot.moving_avg_200d) is not None and _num(snapshot.moving_avg_20d) > _num(snapshot.moving_avg_200d), {"ma20": _num(snapshot.moving_avg_20d), "ma200": _num(snapshot.moving_avg_200d)}, "20DMA above 200DMA"),
    ]
    fail_count = sum(1 for item in evaluations if item["status"] == "fail")
    score = weighted_score(snapshot, raw, criteria)
    return {
        "evaluations": evaluations,
        "summary": {"pass": len(evaluations) - fail_count, "fail": fail_count, "verdict": "PASS" if fail_count == 0 else "FAIL"},
        "score": score if fail_count == 0 else 0,
    }


def weighted_score(snapshot, raw: dict, criteria: dict) -> float:
    revenue = min(max((_num(snapshot.revenue_growth_yoy) or 0) / 25, 0), 1) * 30
    margin = min(max((_num(snapshot.profit_margin) or 0) / 30, 0), 1) * 25
    eps_hist = _history(raw, "eps_history")
    eps_score = 25 if len(eps_hist) >= 5 and eps_hist[-1] > eps_hist[0] else 0
    debt = (1 - min(max((_num(snapshot.debt_to_equity) or 1), 0), 1)) * 20
    return round(revenue + margin + eps_score + debt, 2)
