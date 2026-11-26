"""Standard success and error response envelopes for API responses."""

from collections.abc import Mapping
from typing import Any, Generic, Literal, TypeVar

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Envelope returned by the API for successful requests."""

    success: Literal[True] = True
    message: str
    details: T


class ErrorResponse(BaseModel):
    """Envelope returned by the API for failed requests."""

    success: Literal[False] = False
    message: str
    details: Any = None


def success_response(
    details: Any = None,
    message: str = "Request successful",
) -> dict[str, Any]:
    """Build the success payload for a route to return.

    Returns a plain dict on purpose: the route's response_model validates it,
    and FastAPI can read ORM objects placed in `details`.
    """
    return {"success": True, "message": message, "details": details}


def error_response(
    message: str = "Request failed",
    details: Any = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Build the standard error response with its HTTP status code."""
    body = ErrorResponse(message=message, details=details)
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(body),
        headers=headers,
    )


VALIDATION_ERROR_RESPONSE: dict[int, dict[str, Any]] = {
    422: {
        "model": ErrorResponse,
        "description": "Request validation failed",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Validation failed",
                    "details": [
                        {
                            "field": "coordinates.latitude",
                            "message": "Input should be less than or equal to 90",
                        }
                    ],
                }
            }
        },
    }
}

NOT_FOUND_RESPONSE: dict[int, dict[str, Any]] = {
    404: {
        "model": ErrorResponse,
        "description": "Address not found",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": (
                        "Address 3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f "
                        "not found"
                    ),
                    "details": None,
                }
            }
        },
    }
}

SERVER_ERROR_RESPONSE: dict[int, dict[str, Any]] = {
    500: {
        "model": ErrorResponse,
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Internal server error",
                    "details": None,
                }
            }
        },
    }
}
