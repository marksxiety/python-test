"""Tests for address model defaults and derived coordinates."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.address import Address


def test_uuid_and_timestamps_are_set_on_insert(db_session: Session) -> None:
    """Inserting an address generates its UUID and UTC timestamp values."""
    address = Address(
        name="Sample Address",
        street="1 Main Street",
        city="Manila",
        province="Metro Manila",
        postal_code="1000",
        country="Philippines",
        latitude=14.5995,
        longitude=120.9842,
    )

    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)

    assert isinstance(address.id, UUID)
    assert isinstance(address.created_at, datetime)
    assert isinstance(address.updated_at, datetime)
    created_at = address.updated_at

    address.city = "Cebu City"
    db_session.commit()
    db_session.refresh(address)

    assert address.updated_at >= created_at


def test_coordinates_property_returns_nested_values() -> None:
    """The model exposes flat coordinate columns in the API's nested shape."""
    address = Address(latitude=14.5995, longitude=120.9842)

    assert address.coordinates == {"latitude": 14.5995, "longitude": 120.9842}
