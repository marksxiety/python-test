"""Direct database-session tests for address services."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import AddressNotFoundError
from app.schemas.address import AddressCreate, AddressUpdate
from app.services import address as address_service


def _address_data(
    name: str = "Sample Address",
    latitude: float = 14.5995,
    longitude: float = 120.9842,
) -> AddressCreate:
    """Create validated address data for service tests."""
    return AddressCreate(
        name=name,
        street="1 Main Street",
        city="Manila",
        province="Metro Manila",
        postal_code="1000",
        country="Philippines",
        coordinates={"latitude": latitude, "longitude": longitude},
    )


def test_create_get_and_list_addresses(db_session: Session) -> None:
    """Address services create, retrieve, and paginate persisted records."""
    first = address_service.create_address(db_session, _address_data("First Address"))
    second = address_service.create_address(db_session, _address_data("Second Address"))

    assert isinstance(first.id, UUID)
    assert address_service.get_address(db_session, first.id).name == "First Address"
    assert address_service.list_addresses(db_session, skip=1, limit=1) == [second]


def test_get_address_raises_for_unknown_id(db_session: Session) -> None:
    """Missing address identifiers raise the domain not-found exception."""
    with pytest.raises(AddressNotFoundError):
        address_service.get_address(db_session, uuid4())


def test_update_changes_only_supplied_fields(db_session: Session) -> None:
    """Partial service updates preserve omitted fields and clear nullable ones."""
    address = address_service.create_address(db_session, _address_data())

    updated = address_service.update_address(
        db_session,
        address.id,
        AddressUpdate(city="Cebu City", postal_code=None),
    )

    assert updated.city == "Cebu City"
    assert updated.postal_code is None
    assert updated.name == "Sample Address"


def test_delete_address_and_missing_id(db_session: Session) -> None:
    """Delete removes an address and a repeated delete raises not found."""
    address = address_service.create_address(db_session, _address_data())

    address_service.delete_address(db_session, address.id)

    with pytest.raises(AddressNotFoundError):
        address_service.delete_address(db_session, address.id)


def test_find_within_distance_filters_and_orders_addresses(
    db_session: Session,
) -> None:
    """SQL distance search returns only in-radius addresses, nearest first."""
    for name, latitude, longitude in (
        ("Center", 14.5995, 120.9842),
        ("Near", 14.605, 120.99),
        ("Far", 14.8, 121.0),
    ):
        address_service.create_address(
            db_session,
            _address_data(name, latitude, longitude),
        )

    addresses = address_service.find_within_distance(
        db_session,
        latitude=14.5995,
        longitude=120.9842,
        distance_km=10,
    )

    assert [address.name for address in addresses] == ["Center", "Near"]
