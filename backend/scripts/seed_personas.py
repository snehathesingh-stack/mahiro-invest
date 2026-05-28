"""
Seed script — inserts the canonical 'Dad — Long-term Quality' persona into the DB.

Run from backend/ directory:
    python -m scripts.seed_personas

Idempotent: if persona with the same name+owner already exists, it's updated.
"""
from __future__ import annotations

import logging

from app.database import SessionLocal
from app.models import Persona

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DAD_PERSONA_CONFIG = {
    "name": "Dad — Long-term Quality",
    "style": "long_term",
    "hard_filters": {
        "market_cap_cr": {"min": 5000},
        "pe_ratio": {"min": 20, "max": 25},
        "revenue_growth_yoy_pct": {"min": 10, "sustained_years": 3},
        "profit_margin_pct": {"min": 10},
        "eps_trend": {"must_increase_yoy": True, "lookback_years": 3},
        "working_capital_ratio": {"min": 2},
        "quick_ratio": {"min": 1},
        "debt_to_equity": {"max": 1},
        "pb_ratio": {"max": 2},
        "debtor_days": {"max": 100},
        "public_holding_pct": {"max": 35},
        "cash_flow": {"positive": True, "growing_yoy": True},
        "fii_dii_holding": {"trend": "increasing"},
        "moving_average_signal": {"golden_cross_20_200": True},
        "roe_pct": {"min": 15},
        "avg_volume_10d": {"min": 100000},
    },
    "ranking_weights": {
        "revenue_growth_yoy_pct": 0.25,
        "profit_margin_pct": 0.20,
        "eps_growth_pct": 0.20,
        "debt_to_equity_inverse": 0.15,
        "roe_pct": 0.20,
    },
    "bonus_points": {
        "dividend_paying": 5,
        "preferred_sectors": ["IT", "Finance", "Railway", "Automobile", "FMCG"],
    },
    "portfolio_alerts": {"on_hard_filter_violation": "sell_immediately"},
    "earnings_strategy": {"alert_window_days": 7, "action": "buy_before_if_criteria_met"},
}


def seed():
    db = SessionLocal()
    try:
        existing = (
            db.query(Persona)
            .filter(Persona.name == "Dad — Long-term Quality", Persona.owner == "dad")
            .first()
        )
        if existing:
            logger.info(f"Persona already exists (id={existing.id}). Updating config.")
            existing.style = "long_term"
            existing.config = DAD_PERSONA_CONFIG
        else:
            persona = Persona(
                name="Dad — Long-term Quality",
                owner="dad",
                style="long_term",
                config=DAD_PERSONA_CONFIG,
            )
            db.add(persona)
            logger.info("Created new persona: Dad — Long-term Quality")
        db.commit()
        logger.info("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()