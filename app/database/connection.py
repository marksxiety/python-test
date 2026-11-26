"""SQLAlchemy engine, declarative base, and session dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class that collects SQLAlchemy model metadata."""


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and always close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create the tables registered with the shared declarative base."""
    from app.models import Address  # local import avoids a circular import

    _ = Address
    Base.metadata.create_all(bind=engine)
