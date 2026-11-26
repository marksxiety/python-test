"""Domain exception types and their HTTP exception-handler registration."""

from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import print_logging
from app.core.responses import error_response


class AddressNotFoundError(Exception):
    """Indicate that an address identified by UUID does not exist."""

    def __init__(self, address_id: UUID) -> None:
        """Store the missing address identifier for HTTP error reporting."""
        self.address_id = address_id
        super().__init__(str(address_id))


def _validation_details(errors: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Convert validation errors into JSON-serializable field/message pairs."""
    details: list[dict[str, str]] = []
    for error in errors:
        location = error.get("loc") or ()
        field = ".".join(str(part) for part in location[1:]) or "body"
        details.append(
            {
                "field": field,
                "message": str(error.get("msg", "Invalid value")),
            }
        )
    return details


async def _address_not_found_handler(
    request: Request,
    exception: AddressNotFoundError,
) -> JSONResponse:
    """Return the standard not-found response for a missing address."""
    print_logging(
        "warning",
        f"{request.method} {request.url.path}: "
        f"address {exception.address_id} not found",
    )
    return error_response(
        message=f"Address {exception.address_id} not found",
        details=None,
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def _validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    """Return field-level validation details in the standard envelope."""
    details = _validation_details(exception.errors())
    print_logging(
        "warning",
        f"{request.method} {request.url.path}: validation failed",
    )
    return error_response(
        message="Validation failed",
        details=details,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


async def _http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
) -> JSONResponse:
    """Wrap framework HTTP errors in the standard envelope."""
    if exception.status_code == status.HTTP_404_NOT_FOUND:
        print_logging(
            "warning",
            f"{request.method} {request.url.path}: {exception.detail}",
        )
    return error_response(
        message=str(exception.detail),
        details=None,
        status_code=exception.status_code,
        headers=exception.headers,
    )


async def _unhandled_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Log unexpected failures and return a non-sensitive server error."""
    del request, exception
    print_logging("error", "Unhandled application error")
    return error_response(
        message="Internal server error",
        details=None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide handlers for domain and unexpected errors."""
    app.add_exception_handler(
        RequestValidationError,
        _validation_exception_handler,
    )
    app.add_exception_handler(
        AddressNotFoundError,
        _address_not_found_handler,
    )
    app.add_exception_handler(
        StarletteHTTPException,
        _http_exception_handler,
    )
    app.add_exception_handler(Exception, _unhandled_exception_handler)
