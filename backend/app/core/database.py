"""SQLAlchemy engine + session factory (sync SQLite)."""

from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

_engine = create_engine(
    settings.database_url.replace("sqlite+aiosqlite", "sqlite"),
    connect_args={"check_same_thread": False},
    future=True,
)

SessionLocal = sessionmaker(
    bind=_engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def enable_sqlite_foreign_keys(dbapi_conn, _record):
    dbapi_conn.execute("PRAGMA foreign_keys = ON")


event.listen(_engine, "connect", enable_sqlite_foreign_keys)


def init_db() -> None:
    """Create all tables (idempotent)."""
    from ..models import plugin as _plugin_models  # noqa: F401  registers models
    from ..models import analysis as _analysis_models  # noqa: F401

    Base.metadata.create_all(_engine)


def get_session():
    """FastAPI dependency: yield a DB session and close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()