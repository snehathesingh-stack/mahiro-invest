from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import alerts, auth, earnings, health, personas, portfolio, screener, stocks, watchlists
from app.services.seed import seed_defaults

app = FastAPI(title="Mahiro Invest API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(stocks.router)
app.include_router(personas.router)
app.include_router(auth.router)
app.include_router(screener.router)
app.include_router(portfolio.router)
app.include_router(watchlists.router)
app.include_router(alerts.router)
app.include_router(earnings.router)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_defaults(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Mahiro Invest API. See /docs"}
