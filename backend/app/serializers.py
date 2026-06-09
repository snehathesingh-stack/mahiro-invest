from __future__ import annotations


def stock_dict(stock, snapshot=None) -> dict:
    data = {
        "id": stock.id,
        "symbol": stock.symbol,
        "company_name": stock.company_name,
        "sector": stock.sector,
        "market_cap": float(stock.market_cap) if stock.market_cap is not None else None,
        "market_cap_cr": stock.market_cap_cr,
        "last_price": float(stock.last_price) if stock.last_price is not None else None,
        "last_updated": stock.last_updated.isoformat() if stock.last_updated else None,
    }
    if snapshot:
        data["latest_fundamentals"] = snapshot_dict(snapshot)
    return data


def snapshot_dict(snapshot) -> dict:
    return {
        "id": snapshot.id,
        "snapshot_date": snapshot.snapshot_date.isoformat() if snapshot.snapshot_date else None,
        "pe_ratio": _f(snapshot.pe_ratio),
        "eps": _f(snapshot.eps),
        "roe": _f(snapshot.roe),
        "debt_to_equity": _f(snapshot.debt_to_equity),
        "revenue_growth_yoy": _f(snapshot.revenue_growth_yoy),
        "profit_margin": _f(snapshot.profit_margin),
        "cash_flow_from_operations": _f(snapshot.cash_flow_from_operations),
        "cash_flow_positive": snapshot.cash_flow_positive,
        "debtor_days": _f(snapshot.debtor_days),
        "fii_holding_pct": _f(snapshot.fii_holding_pct),
        "dii_holding_pct": _f(snapshot.dii_holding_pct),
        "public_holding_pct": _f(getattr(snapshot, "public_holding_pct", None)),
        "moving_avg_20d": _f(snapshot.moving_avg_20d),
        "moving_avg_200d": _f(snapshot.moving_avg_200d),
        "dividend_yield": _f(snapshot.dividend_yield),
        "raw_json": snapshot.raw_json or {},
        "source": snapshot.source,
        "fetched_at": snapshot.fetched_at.isoformat() if snapshot.fetched_at else None,
    }


def persona_dict(persona) -> dict:
    return {
        "id": persona.id,
        "user_id": persona.user_id,
        "name": persona.name,
        "description": persona.description,
        "criteria": persona.criteria,
        "created_at": persona.created_at.isoformat() if persona.created_at else None,
        "updated_at": persona.updated_at.isoformat() if persona.updated_at else None,
    }


def _f(value):
    return float(value) if value is not None else None
