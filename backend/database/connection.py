"""
Database Connection

Creates:

- SQLAlchemy Engine
- Session Factory

Used throughout the project.

Author: HireEZ
"""

import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import config


ssl_params = {}
# PlanetScale and other cloud MySQL providers require SSL
if os.getenv("DB_SSL", "").lower() in ("true", "1", "yes"):
    ssl_params = {
        "connect_args": {
            "ssl": {
                "rejectUnauthorized": True,
            }
        }
    }


DATABASE_URL = (
    f"mysql+pymysql://"
    f"{quote_plus(config.DB_USER)}:"
    f"{quote_plus(config.DB_PASSWORD)}@"
    f"{config.DB_HOST}:"
    f"{config.DB_PORT}/"
    f"{config.DB_NAME}"
    f"?ssl={'rejectUnauthorized=True' if os.getenv('DB_SSL', '').lower() in ('true','1','yes') else ''}"
)


engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
    **ssl_params,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    Dependency used by FastAPI.

    Creates one database session per request.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
