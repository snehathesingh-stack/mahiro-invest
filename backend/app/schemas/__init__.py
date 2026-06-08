from __future__ import annotations

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PersonaRequest(BaseModel):
    name: str
    description: str | None = None
    criteria: dict


class ScreenerRunRequest(BaseModel):
    persona_id: int
    symbols: list[str] | None = None


class HoldingRequest(BaseModel):
    symbol: str
    quantity: float
    avg_buy_price: float


class WatchlistRequest(BaseModel):
    name: str
    stock_ids: list[str] = []
