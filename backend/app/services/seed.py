from __future__ import annotations

from app.models import Persona, Stock, User
from app.services.defaults import DAD_PERSONA_CRITERIA, DAD_PERSONA_NAME, NIFTY_500_SEED, sample_fundamentals
from app.services.security import hash_password


def seed_defaults(db) -> None:
    user = db.query(User).filter(User.email == "dad@example.com").first()
    if not user:
        user = User(email="dad@example.com", name="Dad", password_hash=hash_password("mahiro123"))
        db.add(user)
        db.flush()

    persona = db.query(Persona).filter(Persona.user_id == user.id, Persona.name == DAD_PERSONA_NAME).first()
    if not persona:
        db.add(
            Persona(
                user_id=user.id,
                name=DAD_PERSONA_NAME,
                description="Strict long-term quality workflow where any hard-filter failure rejects the stock.",
                criteria=DAD_PERSONA_CRITERIA,
            )
        )

    for symbol, name, sector in NIFTY_500_SEED:
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            sample = sample_fundamentals(symbol)
            db.add(
                Stock(
                    symbol=symbol,
                    company_name=name,
                    sector=sector,
                    market_cap=sample["market_cap_cr"] * 10_000_000,
                    last_price=sample["last_price"],
                )
            )
    db.commit()
