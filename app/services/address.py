"""Address CRUD and coordinate-based search business logic."""

from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.constants import EARTH_RADIUS_KM, KM_PER_DEGREE_LATITUDE
from app.core.exceptions import AddressNotFoundError
from app.core.logging import print_logging
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate


def create_address(db: Session, data: AddressCreate) -> Address:
    """Create and return an address from its validated request data."""
    address = Address(
        name=data.name,
        street=data.street,
        city=data.city,
        province=data.province,
        postal_code=data.postal_code,
        country=data.country,
        latitude=data.coordinates.latitude,
        longitude=data.coordinates.longitude,
    )
    try:
        db.add(address)
        db.commit()
        db.refresh(address)
    except Exception:
        db.rollback()
        print_logging("error", "Failed to create address")
        raise

    print_logging("info", f"Created address {address.id}")
    return address


def get_address(db: Session, address_id: UUID) -> Address:
    """Return one address or raise a domain error when it is missing."""
    try:
        address = db.scalar(select(Address).where(Address.id == address_id))
    except Exception:
        db.rollback()
        print_logging("error", f"Failed to retrieve address {address_id}")
        raise

    if address is None:
        print_logging("warning", f"Address {address_id} not found")
        raise AddressNotFoundError(address_id)
    return address


def list_addresses(db: Session, skip: int, limit: int) -> list[Address]:
    """Return a stable, paginated list of saved addresses."""
    print_logging(
        "debug",
        f"Listing addresses with skip={skip} and limit={limit}",
    )
    try:
        statement = (
            select(Address)
            .order_by(Address.created_at, Address.id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())
    except Exception:
        db.rollback()
        print_logging("error", "Failed to list addresses")
        raise


def update_address(
    db: Session,
    address_id: UUID,
    data: AddressUpdate,
) -> Address:
    """Apply the fields supplied in a partial address update."""
    try:
        address = db.scalar(select(Address).where(Address.id == address_id))
    except Exception:
        db.rollback()
        print_logging(
            "error",
            f"Failed to retrieve address {address_id} for update",
        )
        raise

    if address is None:
        print_logging("warning", f"Address {address_id} not found")
        raise AddressNotFoundError(address_id)

    try:
        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "coordinates":
                address.latitude = value["latitude"]
                address.longitude = value["longitude"]
            else:
                setattr(address, field, value)

        db.commit()
        db.refresh(address)
    except Exception:
        db.rollback()
        print_logging("error", f"Failed to update address {address_id}")
        raise

    print_logging("info", f"Updated address {address.id}")
    return address


def delete_address(db: Session, address_id: UUID) -> None:
    """Delete one address or raise a domain error when it is missing."""
    try:
        address = db.scalar(select(Address).where(Address.id == address_id))
    except Exception:
        db.rollback()
        print_logging(
            "error",
            f"Failed to retrieve address {address_id} for deletion",
        )
        raise

    if address is None:
        print_logging("warning", f"Address {address_id} not found")
        raise AddressNotFoundError(address_id)

    try:
        db.delete(address)
        db.commit()
    except Exception:
        db.rollback()
        print_logging("error", f"Failed to delete address {address_id}")
        raise

    print_logging("info", f"Deleted address {address_id}")


def _latitude_bounds(latitude: float, distance_km: float) -> tuple[float, float]:
    """Calculate the indexed latitude bounds for a search radius."""
    lat_delta = distance_km / KM_PER_DEGREE_LATITUDE
    return latitude - lat_delta, latitude + lat_delta


def find_within_distance(
    db: Session,
    latitude: float,
    longitude: float,
    distance_km: float,
) -> list[Address]:
    """Return addresses within a radius, ordered by exact distance."""
    min_lat, max_lat = _latitude_bounds(latitude, distance_km)
    statement = select(Address).from_statement(
        text(
            """
            SELECT id, name, street, city, province, postal_code, country,
                   latitude, longitude, created_at, updated_at
            FROM (
                SELECT addresses.*,
                    :earth_radius * 2 * asin(sqrt(
                        power(sin(radians(latitude - :lat) / 2), 2)
                        + cos(radians(:lat)) * cos(radians(latitude))
                          * power(sin(radians(longitude - :lon) / 2), 2)
                    )) AS distance_km
                FROM addresses
                WHERE latitude BETWEEN :min_lat AND :max_lat
            )
            WHERE distance_km <= :radius
            ORDER BY distance_km
            """
        )
    )

    print_logging(
        "debug",
        f"Searching addresses within a radius of {distance_km} km",
    )
    try:
        addresses = db.scalars(
            statement,
            {
                "earth_radius": EARTH_RADIUS_KM,
                "lat": latitude,
                "lon": longitude,
                "min_lat": min_lat,
                "max_lat": max_lat,
                "radius": distance_km,
            },
        ).all()
        return list(addresses)
    except Exception:
        db.rollback()
        print_logging("error", "Failed to search addresses within a distance")
        raise
