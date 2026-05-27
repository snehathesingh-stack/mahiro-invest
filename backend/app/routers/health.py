from fastapi import APIRouter
from app.database import check_db_connection

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "mahiro-invest-backend",
        "db_connected": check_db_connection(),
    }