"""HTTP tests for the unified exception responses."""

from typing import Any

from fastapi.testclient import TestClient


def _assert_error_envelope(body: dict[str, Any], message: str) -> None:
    """Assert an error response uses exactly the three envelope keys."""
    assert set(body) == {"success", "message", "details"}
    assert body["success"] is False
    assert body["message"] == message
    assert body["details"] is None


def test_unknown_path_returns_404_envelope(client: TestClient) -> None:
    """Unknown paths are wrapped by the HTTP exception handler."""
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    _assert_error_envelope(response.json(), "Not Found")


def test_wrong_method_returns_405_envelope(client: TestClient) -> None:
    """Wrong HTTP methods are wrapped and keep the Allow header."""
    response = client.delete("/api/v1/addresses")

    assert response.status_code == 405
    _assert_error_envelope(response.json(), "Method Not Allowed")
    assert response.headers["allow"]
