"""Database engine and session management.

The engine is created lazily. Nothing here opens a connection at import time,
so an unreachable database no longer prevents the application from starting:
the process boots, /health answers, and data endpoints return 503 until the
database comes back.
"""

import os

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from logging_config import logger


def _database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        return None
    # SQLAlchemy dropped the postgres:// alias; some providers still hand it out.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine():
    """Create the engine on first use. Raises RuntimeError if unconfigured."""
    global _engine
    if _engine is None:
        url = _database_url()
        if not url:
            raise RuntimeError("DATABASE_URL is not set in environment variables")
        # pool_pre_ping discards connections a cloud provider has closed under us,
        # which is the usual cause of intermittent 500s on hosted Postgres.
        _engine = create_engine(url, pool_pre_ping=True, pool_recycle=300)
    return _engine


def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """FastAPI dependency. Returns 503 rather than 500 when the DB is down."""
    try:
        session = get_sessionmaker()()
    except (RuntimeError, SQLAlchemyError) as exc:
        logger.error("Database unavailable: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    try:
        yield session
    finally:
        session.close()


def init_models():
    """Register models and create missing tables. Call this at startup."""
    from models.user import User  # noqa: F401
    from models.paper import Paper  # noqa: F401
    from models.review import Review  # noqa: F401
    from models.conference import Conference  # noqa: F401
    from models.conference_paper import ConferencePaper  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def check_connection():
    """Return (ok, detail) describing current database reachability."""
    from sqlalchemy import text

    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as exc:  # noqa: BLE001 - surfaced verbatim on /health/db
        return False, f"{type(exc).__name__}: {exc}"
