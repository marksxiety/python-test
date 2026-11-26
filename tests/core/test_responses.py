"""Unit tests for the shared response envelopes."""

import json

from app.core.responses import (
    ErrorResponse,
    SuccessResponse,
    error_response,
    success_response,
)


def test_success_response_builds_envelope() -> None:
    """Success payloads expose exactly success, message, and details."""
    payload = success_response(
        details={"id": "123"},
        message="Created",
    )

    assert payload == {
        "success": True,
        "message": "Created",
        "details": {"id": "123"},
    }
    assert set(payload) == {"success", "message", "details"}


def test_success_response_defaults() -> None:
    """Success payloads default to a generic message and empty details."""
    assert success_response() == {
        "success": True,
        "message": "Request successful",
        "details": None,
    }


def test_error_response_builds_json_response() -> None:
    """Error responses carry the envelope and the requested status code."""
    response = error_response(
        message="Address not found",
        details=None,
        status_code=404,
    )

    assert response.status_code == 404
    assert json.loads(response.body) == {
        "success": False,
        "message": "Address not found",
        "details": None,
    }


def test_envelope_models_use_literal_success_flags() -> None:
    """The Pydantic models pin success to True or False."""
    assert SuccessResponse[dict](message="ok", details={}).success is True
    assert ErrorResponse(message="no").success is False
