from __future__ import annotations

from app.models import FundamentalSnapshot, Holding, Persona, Stock, User, Watchlist
from app.services.defaults import QUALITY_PERSONA_CRITERIA, QUALITY_PERSONA_NAME, sample_fundamentals
from app.services.nse_universe import fetch_nse_equity_universe
from app.services.security import hash_password


def sync_stock_universe(db) -> dict:
    added = 0
    existing = 0
    total = 0
    for symbol, name, sector in fetch_nse_equity_universe():
        total += 1
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        sample = sample_fundamentals(symbol)
        if not stock:
            stock = Stock(
                symbol=symbol,
                company_name=name,
                sector=sector,
                market_cap=sample["market_cap_cr"] * 10_000_000,
                last_price=sample["last_price"],
            )
            db.add(stock)
            db.flush()
            added += 1
        else:
            existing += 1
            stock.company_name = name or stock.company_name
            stock.sector = sector or stock.sector
        if not db.query(FundamentalSnapshot).filter(FundamentalSnapshot.stock_id == stock.id).first():
            db.add(FundamentalSnapshot(stock_id=stock.id, source="sample", **sample["snapshot"]))
    db.commit()
    return {"total": total, "added": added, "existing": existing}


def seed_defaults(db) -> None:
    demo_users = [
        ("investor@example.com", "Investor"),
        ("mumma@example.com", "Mumma"),
    ]
    users: list[User] = []
    for email, name in demo_users:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name=name, password_hash=hash_password("mahiro123"))
            db.add(user)
            db.flush()
        users.append(user)

    for user in users:
        persona = db.query(Persona).filter(Persona.user_id == user.id, Persona.name == QUALITY_PERSONA_NAME).first()
        if not persona:
            db.add(
                Persona(
                    user_id=user.id,
                    name=QUALITY_PERSONA_NAME,
                    description="Strict long-term quality workflow where any hard-filter failure rejects the stock.",
                    criteria=QUALITY_PERSONA_CRITERIA,
                )
            )

    sync_stock_universe(db)

    investor = users[0]
    demo_holds = [("HINDUNILVR.NS", 8, 2320), ("INFY.NS", 12, 1420), ("SBIN.NS", 20, 620)]
    for symbol, quantity, avg_buy_price in demo_holds:
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if stock and not db.query(Holding).filter(Holding.user_id == investor.id, Holding.stock_id == stock.id).first():
            db.add(Holding(user_id=investor.id, stock_id=stock.id, quantity=quantity, avg_buy_price=avg_buy_price))

    if not db.query(Watchlist).filter(Watchlist.user_id == investor.id, Watchlist.name == "Quality Watchlist").first():
        db.add(Watchlist(user_id=investor.id, name="Quality Watchlist", stock_ids=["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "TITAN.NS"]))
    db.commit()
