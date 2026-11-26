"""Shared database, session, client, and request-data fixtures."""

import logging
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base, get_db
from app.main import app
from app.models.address import Address


@pytest.fixture(autouse=True)
def _disable_file_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep test runs from writing to the real application log directory."""

    def test_logger() -> logging.Logger:
        """Return a handler-less logger for tests."""
        return logging.getLogger("test.app")

    monkeypatch.setattr("app.core.logging.setup_logging", test_logger)
    monkeypatch.setattr("app.main.setup_logging", test_logger)


@pytest.fixture
def engine() -> Generator[Engine, None, None]:
    """Provide an isolated in-memory SQLite engine for each test."""
    _ = Address
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        yield test_engine
    finally:
        Base.metadata.drop_all(test_engine)
        test_engine.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build sessions bound to the test engine."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture
def db_session(
    engine: Engine,
    session_factory: sessionmaker[Session],
) -> Generator[Session, None, None]:
    """Create the schema and yield a session for direct service tests."""
    Base.metadata.create_all(engine)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def _override_get_db(
    session_factory: sessionmaker[Session],
) -> Generator[Session, None, None]:
    """Yield a test database session for one HTTP request."""
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(
    engine: Engine,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """Provide a TestClient whose requests use the isolated test database."""
    Base.metadata.create_all(engine)
    monkeypatch.setattr("app.database.connection.engine", engine)

    def override_get_db() -> Generator[Session, None, None]:
        yield from _override_get_db(session_factory)

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client_without_raising(
    engine: Engine,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """Provide a TestClient that returns 500 responses instead of raising."""
    Base.metadata.create_all(engine)
    monkeypatch.setattr("app.database.connection.engine", engine)

    def override_get_db() -> Generator[Session, None, None]:
        yield from _override_get_db(session_factory)

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def address_payload() -> dict[str, Any]:
    """Provide a valid address request body for route tests."""
    return {
        "name": "Sample Address",
        "street": "1 Main Street",
        "city": "Manila",
        "province": "Metro Manila",
        "postal_code": "1000",
        "country": "Philippines",
        "coordinates": {"latitude": 14.5995, "longitude": 120.9842},
    }
