from __future__ import annotations

from app.models import FundamentalSnapshot, Holding
from app.services.screener_engine import evaluate_stock


def active_alerts(db, user, persona) -> list[dict]:
    alerts = []
    holdings = db.query(Holding).filter(Holding.user_id == user.id).all()
    for holding in holdings:
        snap = (
            db.query(FundamentalSnapshot)
            .filter(FundamentalSnapshot.stock_id == holding.stock_id)
            .order_by(FundamentalSnapshot.fetched_at.desc())
            .first()
        )
        if not snap:
            continue
        evaluation = evaluate_stock(holding.stock, snap, persona.criteria)
        failures = [item for item in evaluation["evaluations"] if item["status"] == "fail"]
        if failures:
            alerts.append(
                {
                    "holding_id": holding.id,
                    "symbol": holding.stock.symbol,
                    "company_name": holding.stock.company_name,
                    "severity": "critical",
                    "flag": "SELL IMMEDIATELY",
                    "failures": failures,
                }
            )
    return alerts
