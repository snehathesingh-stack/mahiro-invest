from __future__ import annotations

import logging

from app.database import SessionLocal
from app.services.seed import seed_defaults

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed():
    db = SessionLocal()
    try:
        seed_defaults(db)
        logger.info("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
