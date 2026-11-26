"""Version 1 address HTTP endpoints."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.constants import MAX_SEARCH_DISTANCE_KM
from app.core.responses import (
    NOT_FOUND_RESPONSE,
    SERVER_ERROR_RESPONSE,
    SuccessResponse,
    VALIDATION_ERROR_RESPONSE,
    success_response,
)
from app.database.connection import get_db
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate
from app.services import address as address_service

_SAMPLE_ADDRESS: dict[str, Any] = {
    "name": "Home",
    "street": "123 Rizal St",
    "city": "Calauan",
    "province": "Laguna",
    "postal_code": "4012",
    "country": "Philippines",
    "coordinates": {"latitude": 14.1472, "longitude": 121.3167},
    "id": "3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f",
    "created_at": "2026-11-26T10:30:00",
    "updated_at": "2026-11-26T10:30:00",
}


def _success_response_example(
    status_code: int,
    message: str,
    details: Any,
) -> dict[int, dict[str, Any]]:
    """Build the Swagger example for a successful route response."""
    return {
        status_code: {
            "description": message,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": message,
                        "details": details,
                    }
                }
            },
        }
    }


router = APIRouter(
    responses={
        **VALIDATION_ERROR_RESPONSE,
        **SERVER_ERROR_RESPONSE,
    }
)


@router.post(
    "/addresses",
    response_model=SuccessResponse[AddressResponse],
    status_code=status.HTTP_201_CREATED,
    responses=_success_response_example(
        201,
        "Address created",
        _SAMPLE_ADDRESS,
    ),
    summary="Create an address",
)
def create_address(
    data: AddressCreate,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Create and persist a validated address."""
    address = address_service.create_address(db, data)
    return success_response(
        details=AddressResponse.model_validate(address),
        message="Address created",
    )


@router.get(
    "/addresses",
    response_model=SuccessResponse[list[AddressResponse]],
    status_code=status.HTTP_200_OK,
    responses=_success_response_example(
        200,
        "Addresses retrieved",
        [_SAMPLE_ADDRESS],
    ),
    summary="List addresses",
)
def list_addresses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return a page of saved addresses."""
    addresses = address_service.list_addresses(db, skip, limit)
    return success_response(
        details=[
            AddressResponse.model_validate(address) for address in addresses
        ],
        message="Addresses retrieved",
    )


@router.get(
    "/addresses/nearby",
    response_model=SuccessResponse[list[AddressResponse]],
    status_code=status.HTTP_200_OK,
    responses=_success_response_example(
        200,
        "Nearby addresses retrieved",
        [_SAMPLE_ADDRESS],
    ),
    summary="Find nearby addresses",
)
def find_nearby_addresses(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    distance_km: float = Query(..., gt=0, le=MAX_SEARCH_DISTANCE_KM),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return addresses near the supplied coordinate."""
    addresses = address_service.find_within_distance(
        db,
        latitude,
        longitude,
        distance_km,
    )
    return success_response(
        details=[
            AddressResponse.model_validate(address) for address in addresses
        ],
        message="Nearby addresses retrieved",
    )


@router.get(
    "/addresses/{address_id}",
    response_model=SuccessResponse[AddressResponse],
    status_code=status.HTTP_200_OK,
    responses={
        **NOT_FOUND_RESPONSE,
        **_success_response_example(
            200,
            "Address retrieved",
            _SAMPLE_ADDRESS,
        ),
    },
    summary="Get an address",
)
def get_address(
    address_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one address by its UUID."""
    address = address_service.get_address(db, address_id)
    return success_response(
        details=AddressResponse.model_validate(address),
        message="Address retrieved",
    )


@router.patch(
    "/addresses/{address_id}",
    response_model=SuccessResponse[AddressResponse],
    status_code=status.HTTP_200_OK,
    responses={
        **NOT_FOUND_RESPONSE,
        **_success_response_example(
            200,
            "Address updated",
            _SAMPLE_ADDRESS,
        ),
    },
    summary="Update an address",
)
def update_address(
    address_id: UUID,
    data: AddressUpdate,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Update only the supplied address fields."""
    address = address_service.update_address(db, address_id, data)
    return success_response(
        details=AddressResponse.model_validate(address),
        message="Address updated",
    )


@router.delete(
    "/addresses/{address_id}",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    responses={
        **NOT_FOUND_RESPONSE,
        **_success_response_example(
            200,
            "Address deleted",
            None,
        ),
    },
    summary="Delete an address",
)
def delete_address(
    address_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Delete one address."""
    address_service.delete_address(db, address_id)
    return success_response(details=None, message="Address deleted")
