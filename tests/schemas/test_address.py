"""Tests for address request validation and partial-update schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.address import AddressCreate, AddressUpdate, Coordinates


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [(91, 120), (14, -181)],
)
def test_coordinates_reject_out_of_range_values(
    latitude: float,
    longitude: float,
) -> None:
    """Coordinates outside valid latitude or longitude bounds are rejected."""
    with pytest.raises(ValidationError):
        Coordinates(latitude=latitude, longitude=longitude)


def test_address_create_rejects_blank_street() -> None:
    """Whitespace-only required strings fail after whitespace stripping."""
    with pytest.raises(ValidationError):
        AddressCreate(
            name="Sample Address",
            street=" ",
            city="Manila",
            province="Metro Manila",
            country="Philippines",
            coordinates={"latitude": 14.5995, "longitude": 120.9842},
        )


def test_address_update_contains_only_supplied_fields() -> None:
    """Partial updates preserve omission and trim supplied text."""
    update = AddressUpdate(city=" Cebu City ", postal_code=None)

    assert update.model_dump(exclude_unset=True) == {
        "city": "Cebu City",
        "postal_code": None,
    }
    assert AddressUpdate().model_dump(exclude_unset=True) == {}


def test_address_update_rejects_explicit_nulls() -> None:
    """Required fields cannot be cleared with an explicit null."""
    with pytest.raises(ValidationError):
        AddressUpdate(city=None)

    with pytest.raises(ValidationError):
        AddressUpdate(coordinates=None)


def test_address_create_rejects_unknown_fields() -> None:
    """Typos in payload keys fail validation instead of being ignored."""
    with pytest.raises(ValidationError):
        AddressCreate(
            name="Sample Address",
            street="1 Main Street",
            city="Manila",
            province="Metro Manila",
            country="Philippines",
            coordinates={"latitude": 14.5995, "longitude": 120.9842},
            typo_field="ignored",
        )
