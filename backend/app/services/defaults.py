from __future__ import annotations

from datetime import date, timedelta

QUALITY_PERSONA_NAME = "Long-term Quality Investor"
DAD_PERSONA_NAME = QUALITY_PERSONA_NAME

QUALITY_PERSONA_CRITERIA = {
    "hard_filters": {
        "market_cap_cr": {"min": 5000},
        "pe_ratio": {"enabled": True, "min": 10, "max": 25},
        "eps_trend": {"lookback_years": 5, "must_trend_up": True},
        "revenue_growth_yoy": {"min": 10, "sustained_years": 3},
        "profit_margin": {"positive": True},
        "debt_to_equity": {"max": 1.0},
        "roe": {"min": 15},
        "cash_flow_from_operations": {"positive": True, "growing_yoy": True},
        "debtor_days": {"max": 100},
        "fii_dii_holding": {"both_increasing": True},
        "moving_average_signal": {"ma20_above_ma200": True},
        "dividend_yield": {"nice_to_have": True},
    },
    "ranking_weights": {
        "revenue_growth_yoy": 30,
        "profit_margin": 25,
        "eps_consistency": 25,
        "debt_to_equity": 20,
    },
    "portfolio_alerts": {"on_hard_filter_violation": "SELL IMMEDIATELY"},
    "earnings_strategy": {"buy_decisions": "before_earnings", "post_earnings": "rerun_persona"},
}
DAD_PERSONA_CRITERIA = QUALITY_PERSONA_CRITERIA


def persona_preset(name: str) -> tuple[str, str, dict]:
    key = name.strip().lower()
    criteria = {
        "Conservative": {
            **QUALITY_PERSONA_CRITERIA,
            "hard_filters": {
                **QUALITY_PERSONA_CRITERIA["hard_filters"],
                "market_cap_cr": {"min": 20000},
                "pe_ratio": {"enabled": True, "min": 8, "max": 22},
                "debt_to_equity": {"max": 0.6},
                "roe": {"min": 18},
            },
        },
        "Growth": {
            **QUALITY_PERSONA_CRITERIA,
            "hard_filters": {
                **QUALITY_PERSONA_CRITERIA["hard_filters"],
                "market_cap_cr": {"min": 2000},
                "pe_ratio": {"enabled": False, "min": 0, "max": 60},
                "revenue_growth_yoy": {"min": 18, "sustained_years": 2},
                "roe": {"min": 12},
            },
        },
        "Dividend": {
            **QUALITY_PERSONA_CRITERIA,
            "hard_filters": {
                **QUALITY_PERSONA_CRITERIA["hard_filters"],
                "pe_ratio": {"enabled": True, "min": 6, "max": 28},
                "dividend_yield": {"nice_to_have": False, "min": 1.5},
                "debt_to_equity": {"max": 0.8},
            },
        },
        "Momentum": {
            **QUALITY_PERSONA_CRITERIA,
            "hard_filters": {
                **QUALITY_PERSONA_CRITERIA["hard_filters"],
                "pe_ratio": {"enabled": False, "min": 0, "max": 80},
                "moving_average_signal": {"ma20_above_ma200": True},
                "revenue_growth_yoy": {"min": 12, "sustained_years": 1},
            },
        },
        "Banking-focused": {
            **QUALITY_PERSONA_CRITERIA,
            "hard_filters": {
                **QUALITY_PERSONA_CRITERIA["hard_filters"],
                "market_cap_cr": {"min": 10000},
                "pe_ratio": {"enabled": True, "min": 5, "max": 30},
                "debtor_days": {"max": 100},
                "debt_to_equity": {"max": 2.5},
                "roe": {"min": 12},
            },
        },
    }
    for preset_name, preset_criteria in criteria.items():
        if preset_name.lower() == key:
            return preset_name, f"{preset_name} NSE screening profile.", preset_criteria
    return name, f"{name} custom NSE screening profile.", QUALITY_PERSONA_CRITERIA

NIFTY_500_SEED = [
    ("RELIANCE.NS", "Reliance Industries", "Energy"),
    ("TCS.NS", "Tata Consultancy Services", "Information Technology"),
    ("HDFCBANK.NS", "HDFC Bank", "Financial Services"),
    ("INFY.NS", "Infosys", "Information Technology"),
    ("ICICIBANK.NS", "ICICI Bank", "Financial Services"),
    ("HINDUNILVR.NS", "Hindustan Unilever", "FMCG"),
    ("ITC.NS", "ITC", "FMCG"),
    ("LT.NS", "Larsen & Toubro", "Construction"),
    ("SBIN.NS", "State Bank of India", "Financial Services"),
    ("BHARTIARTL.NS", "Bharti Airtel", "Telecom"),
    ("AXISBANK.NS", "Axis Bank", "Financial Services"),
    ("MARUTI.NS", "Maruti Suzuki India", "Automobile"),
    ("SUNPHARMA.NS", "Sun Pharmaceutical", "Healthcare"),
    ("ASIANPAINT.NS", "Asian Paints", "Consumer Durables"),
    ("TITAN.NS", "Titan Company", "Consumer Durables"),
    ("ULTRACEMCO.NS", "UltraTech Cement", "Cement"),
    ("WIPRO.NS", "Wipro", "Information Technology"),
    ("ONGC.NS", "Oil and Natural Gas Corporation", "Energy"),
    ("POWERGRID.NS", "Power Grid Corporation", "Power"),
    ("NTPC.NS", "NTPC", "Power"),
]


def sample_fundamentals(symbol: str) -> dict:
    base = sum(ord(c) for c in symbol)
    quality = base % 7
    pe = 12 + (base % 24)
    market_cap_cr = 8000 + (base % 150000)
    price = 300 + (base % 3200)
    ma20 = price * (1.02 if quality >= 3 else 0.96)
    ma200 = price
    revenue_growth = 8 + (base % 18)
    eps_history = [18 + quality * 2 + i * (1.5 + quality / 5) for i in range(5)]
    cfo_history = [900 + quality * 80 + i * 120 for i in range(5)]
    return {
        "symbol": symbol.upper(),
        "company_name": next((n for s, n, _ in NIFTY_500_SEED if s == symbol.upper()), symbol.upper()),
        "sector": next((sec for s, _, sec in NIFTY_500_SEED if s == symbol.upper()), "Diversified"),
        "market_cap_cr": market_cap_cr,
        "last_price": price,
        "snapshot": {
            "pe_ratio": pe,
            "eps": eps_history[-1],
            "roe": 12 + quality * 3,
            "debt_to_equity": round(0.25 + (base % 12) / 10, 2),
            "revenue_growth_yoy": revenue_growth,
            "profit_margin": 5 + quality * 4,
            "cash_flow_from_operations": cfo_history[-1],
            "cash_flow_positive": cfo_history[-1] > 0,
            "debtor_days": 45 + (base % 80),
            "fii_holding_pct": 12 + quality,
            "dii_holding_pct": 8 + quality,
            "moving_avg_20d": round(ma20, 2),
            "moving_avg_200d": round(ma200, 2),
            "dividend_yield": round((base % 40) / 10, 2),
            "raw_json": {
                "fallback": True,
                "eps_history": eps_history,
                "revenue_growth_history": [revenue_growth - 2, revenue_growth - 1, revenue_growth],
                "cash_flow_history": cfo_history,
                "fii_history": [10 + quality, 11 + quality, 12 + quality],
                "dii_history": [6 + quality, 7 + quality, 8 + quality],
            },
        },
    }


def fallback_equity_universe() -> list[tuple[str, str, str]]:
    return NIFTY_500_SEED


def sample_earnings(days: int = 90) -> list[dict]:
    today = date.today()
    items = []
    for i, (symbol, name, sector) in enumerate(NIFTY_500_SEED[:16]):
        earnings_date = today + timedelta(days=3 + (i * 5) % max(days, 7))
        items.append(
            {
                "symbol": symbol,
                "company_name": name,
                "sector": sector,
                "earnings_date": earnings_date.isoformat(),
                "is_this_week": (earnings_date - today).days <= 7,
                "rule": "Prepare BUY decisions before earnings",
            }
        )
    return sorted(items, key=lambda item: item["earnings_date"])
