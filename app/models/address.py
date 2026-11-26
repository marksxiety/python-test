"""SQLAlchemy model for persisted address records."""

import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Address(Base):
    """Persist an address and its geographic coordinates."""

    __tablename__ = "addresses"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    province: Mapped[str] = mapped_column(String(120), nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    @property
    def coordinates(self) -> dict[str, float]:
        """Expose lat/lon in the nested shape the API schema expects."""
        return {"latitude": self.latitude, "longitude": self.longitude}
