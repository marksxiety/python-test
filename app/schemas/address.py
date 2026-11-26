"""Pydantic schemas for address requests and responses."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Coordinates(BaseModel):
    """A geographic point in decimal degrees."""

    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class AddressBase(BaseModel):
    """Fields shared by create and response."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=3, max_length=120)
    street: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=120)
    province: str = Field(..., min_length=1, max_length=120)
    postal_code: str | None = Field(None, min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=120)
    coordinates: Coordinates


class AddressCreate(AddressBase):
    """Payload for creating an address."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Home",
                    "street": "123 Rizal St",
                    "city": "Calauan",
                    "province": "Laguna",
                    "postal_code": "4012",
                    "country": "Philippines",
                    "coordinates": {
                        "latitude": 14.1472,
                        "longitude": 121.3167,
                    },
                }
            ]
        },
    )


class AddressUpdate(BaseModel):
    """Payload for a partial update. Only the fields sent are changed."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={"examples": [{"city": "Calauan"}]},
    )

    name: str | None = Field(None, min_length=3, max_length=120)
    street: str | None = Field(None, min_length=1, max_length=255)
    city: str | None = Field(None, min_length=1, max_length=120)
    province: str | None = Field(None, min_length=1, max_length=120)
    postal_code: str | None = Field(None, min_length=1, max_length=20)
    country: str | None = Field(None, min_length=1, max_length=120)
    coordinates: Coordinates | None = None

    @field_validator(
        "name",
        "street",
        "city",
        "province",
        "country",
        "coordinates",
    )
    @classmethod
    def _reject_null_required(cls, value: Any) -> Any:
        """Reject explicit nulls for fields that cannot be cleared.

        Validators do not run for omitted fields, so leaving a required field
        out still performs a partial update.
        """
        if value is None:
            raise ValueError("Field cannot be null")
        return value


class AddressResponse(AddressBase):
    """Address as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
