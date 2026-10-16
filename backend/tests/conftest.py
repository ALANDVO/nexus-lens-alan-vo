"""Shared pytest fixtures for Nexus Lens backend tests.

A throwaway SQLite file is used; tables are created once and rows are cleared
before each test for isolation.
"""

from __future__ import annotations

import os
import tempfile

# Configure test database BEFORE importing app modules.
_test_dir = tempfile.mkdtemp(prefix="nexus_lens_test_")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{os.path.join(_test_dir, 'test.db')}")
os.environ.setdefault("APP_ENV", "testing")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, SessionLocal, _engine, get_session  # noqa: E402
from app.main import create_app  # noqa: E402

# Import models so they register with Base.metadata before create_all.
from app.models.plugin import Plugin  # noqa: E402, F401
from app.models.analysis import (  # noqa: E402, F401
    AnalysisResult,
    AuditLog,
    Finding,
)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create all tables once for the test session."""
    Base.metadata.create_all(_engine)
    yield


@pytest.fixture
def db_session():
    """Yield a SQLAlchemy session, rolling back at teardown."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def clean_tables(db_session):
    """Delete all rows before each test for isolation."""
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    yield


@pytest.fixture
def client(db_session):
    """FastAPI TestClient crossing the real ASGI/HTTP boundary.

    The session dependency is overridden to share the pytest ``db_session``.
    """
    app = create_app()

    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()