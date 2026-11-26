"""Tests for session lifecycle and explicit database initialization."""

from unittest.mock import Mock

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from app.database import connection
from scripts import init_db


def test_get_db_closes_the_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Closing the dependency generator always closes its session."""
    session = Mock()

    def make_session() -> Mock:
        """Return the fake session used to observe dependency cleanup."""
        return session

    monkeypatch.setattr(connection, "SessionLocal", make_session)
    dependency = connection.get_db()

    assert next(dependency) is session
    dependency.close()

    session.close.assert_called_once_with()


def test_init_db_is_idempotent(
    engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Running the explicit initializer repeatedly keeps the same schema."""
    monkeypatch.setattr(connection, "engine", engine)

    init_db.main()
    init_db.main()

    assert inspect(engine).has_table("addresses")
