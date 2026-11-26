"""HTTP contract tests for version 1 address routes."""

from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.services import address as address_service


def _assert_success_envelope(body: dict[str, Any], message: str) -> None:
    """Assert the shared success envelope shape and message."""
    assert set(body) == {"success", "message", "details"}
    assert body["success"] is True
    assert body["message"] == message


def _assert_error_envelope(body: dict[str, Any], message: str) -> None:
    """Assert an error envelope without details."""
    assert set(body) == {"success", "message", "details"}
    assert body["success"] is False
    assert body["message"] == message
    assert body["details"] is None


def _validation_fields(body: dict[str, Any]) -> set[str]:
    """Return the fields reported in a validation response."""
    return {detail["field"] for detail in body["details"]}


def test_create_returns_created_address(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """Create returns HTTP 201 and the created address in the envelope."""
    response = client.post("/api/v1/addresses", json=address_payload)

    assert response.status_code == 201
    body = response.json()
    _assert_success_envelope(body, "Address created")
    UUID(body["details"]["id"])
    assert body["details"]["coordinates"] == {
        "latitude": 14.5995,
        "longitude": 120.9842,
    }


def test_latitude_validation_uses_field_message_details(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """Latitude 91 reports coordinates.latitude as a field/message object."""
    address_payload["coordinates"] = {"latitude": 91, "longitude": 120}

    response = client.post("/api/v1/addresses", json=address_payload)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation failed"
    assert body["details"][0]["field"] == "coordinates.latitude"
    assert set(body["details"][0]) == {"field", "message"}


@pytest.mark.parametrize(
    ("coordinates", "street", "expected_field"),
    [
        ({"latitude": 14, "longitude": -181}, "1 Main Street", "coordinates.longitude"),
        ({"latitude": 14, "longitude": 120}, " ", "street"),
    ],
)
def test_invalid_create_returns_descriptive_422(
    client: TestClient,
    address_payload: dict[str, Any],
    coordinates: dict[str, float],
    street: str,
    expected_field: str,
) -> None:
    """Invalid fields are listed with their field paths."""
    address_payload["coordinates"] = coordinates
    address_payload["street"] = street

    response = client.post("/api/v1/addresses", json=address_payload)

    assert response.status_code == 422
    body = response.json()
    assert body["message"] == "Validation failed"
    assert expected_field in _validation_fields(body)


def test_multiple_create_errors_are_all_listed(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """Multiple invalid fields each appear in the details list."""
    address_payload["street"] = " "
    address_payload["coordinates"] = {"latitude": 91, "longitude": 120}

    response = client.post("/api/v1/addresses", json=address_payload)

    assert response.status_code == 422
    body = response.json()
    assert {"street", "coordinates.latitude"} <= _validation_fields(body)


def test_get_returns_address_and_unknown_id_returns_404(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """GET returns the created address and a missing UUID returns 404."""
    created = client.post("/api/v1/addresses", json=address_payload)
    address_id = created.json()["details"]["id"]
    unknown_id = uuid4()

    response = client.get(f"/api/v1/addresses/{address_id}")
    missing_response = client.get(f"/api/v1/addresses/{unknown_id}")

    assert response.status_code == 200
    body = response.json()
    _assert_success_envelope(body, "Address retrieved")
    assert body["details"]["id"] == address_id

    assert missing_response.status_code == 404
    _assert_error_envelope(
        missing_response.json(),
        f"Address {unknown_id} not found",
    )


def test_patch_updates_only_submitted_fields(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """PATCH changes supplied fields while preserving the rest."""
    created = client.post("/api/v1/addresses", json=address_payload)
    address_id = created.json()["details"]["id"]

    response = client.patch(
        f"/api/v1/addresses/{address_id}",
        json={"city": "Cebu City"},
    )

    assert response.status_code == 200
    body = response.json()
    _assert_success_envelope(body, "Address updated")
    assert body["details"]["city"] == "Cebu City"
    assert body["details"]["name"] == "Sample Address"
    assert body["details"]["coordinates"] == {
        "latitude": 14.5995,
        "longitude": 120.9842,
    }


def test_delete_returns_success_envelope_and_repeated_delete_returns_404(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """DELETE returns a 200 envelope with null details, then 404."""
    created = client.post("/api/v1/addresses", json=address_payload)
    address_id = created.json()["details"]["id"]

    deleted = client.delete(f"/api/v1/addresses/{address_id}")
    missing = client.delete(f"/api/v1/addresses/{address_id}")

    assert deleted.status_code == 200
    body = deleted.json()
    _assert_success_envelope(body, "Address deleted")
    assert body["details"] is None

    assert missing.status_code == 404
    _assert_error_envelope(
        missing.json(),
        f"Address {address_id} not found",
    )


def test_nearby_returns_address_list_nearest_first(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """The nearby route returns an ordered list without distance fields."""
    for name, latitude, longitude in (
        ("Center", 14.5995, 120.9842),
        ("Near", 14.605, 120.99),
        ("Far", 14.8, 121.0),
    ):
        payload = {
            **address_payload,
            "name": name,
            "coordinates": {"latitude": latitude, "longitude": longitude},
        }
        assert client.post("/api/v1/addresses", json=payload).status_code == 201

    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 14.5995,
            "longitude": 120.9842,
            "distance_km": 10,
        },
    )

    assert response.status_code == 200
    body = response.json()
    _assert_success_envelope(body, "Nearby addresses retrieved")
    assert [address["name"] for address in body["details"]] == ["Center", "Near"]
    assert "distance_km" not in body["details"][0]


def test_list_route_applies_pagination(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """The list route returns the requested page in the envelope."""
    for name in ("First Address", "Second Address"):
        payload = {**address_payload, "name": name}
        assert client.post("/api/v1/addresses", json=payload).status_code == 201

    response = client.get("/api/v1/addresses", params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    _assert_success_envelope(body, "Addresses retrieved")
    assert [address["name"] for address in body["details"]] == ["Second Address"]


@pytest.mark.parametrize("params", [{"skip": -1}, {"limit": 0}, {"limit": 101}])
def test_invalid_pagination_returns_422(
    client: TestClient,
    params: dict[str, int],
) -> None:
    """Out-of-range pagination values return validation details."""
    response = client.get("/api/v1/addresses", params=params)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation failed"
    assert _validation_fields(body)


@pytest.mark.parametrize(
    ("params", "expected_field"),
    [
        (
            {"latitude": 91, "longitude": 120, "distance_km": 10},
            "latitude",
        ),
        (
            {"latitude": 14, "longitude": -181, "distance_km": 10},
            "longitude",
        ),
        (
            {"latitude": 14, "longitude": 120, "distance_km": 0},
            "distance_km",
        ),
    ],
)
def test_invalid_nearby_query_returns_422(
    client: TestClient,
    params: dict[str, float],
    expected_field: str,
) -> None:
    """Invalid nearby query values return field-specific details."""
    response = client.get("/api/v1/addresses/nearby", params=params)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert expected_field in _validation_fields(body)


def test_invalid_uuid_returns_422(client: TestClient) -> None:
    """A malformed address identifier returns validation details."""
    response = client.get("/api/v1/addresses/not-a-uuid")

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation failed"
    assert body["details"][0]["field"] == "address_id"


def test_malformed_json_returns_field_message_details(
    client: TestClient,
) -> None:
    """Undecodable JSON still returns a list of field/message details."""
    response = client.post(
        "/api/v1/addresses",
        content="{not json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["message"] == "Validation failed"
    assert isinstance(body["details"], list)
    assert body["details"]
    assert all(set(detail) == {"field", "message"} for detail in body["details"])


def test_unknown_payload_fields_are_rejected(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """Unknown fields fail validation instead of being silently ignored."""
    response = client.post(
        "/api/v1/addresses",
        json={**address_payload, "typo_field": "ignored"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert "typo_field" in _validation_fields(body)


def test_patch_rejects_null_for_required_fields(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """Explicit nulls are rejected for fields that the database requires."""
    created = client.post("/api/v1/addresses", json=address_payload)
    address_id = created.json()["details"]["id"]

    response = client.patch(
        f"/api/v1/addresses/{address_id}",
        json={"city": None},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert "city" in _validation_fields(body)


def test_patch_can_clear_nullable_postal_code(
    client: TestClient,
    address_payload: dict[str, Any],
) -> None:
    """The nullable postal code can be cleared with an explicit null."""
    created = client.post("/api/v1/addresses", json=address_payload)
    address_id = created.json()["details"]["id"]

    response = client.patch(
        f"/api/v1/addresses/{address_id}",
        json={"postal_code": None},
    )

    assert response.status_code == 200
    body = response.json()
    _assert_success_envelope(body, "Address updated")
    assert body["details"]["postal_code"] is None


def test_patch_unknown_id_returns_404(client: TestClient) -> None:
    """Updating a missing address returns the standard not-found envelope."""
    unknown_id = uuid4()

    response = client.patch(
        f"/api/v1/addresses/{unknown_id}",
        json={"city": "Cebu City"},
    )

    assert response.status_code == 404
    _assert_error_envelope(
        response.json(),
        f"Address {unknown_id} not found",
    )


def test_delete_invalid_uuid_returns_422(client: TestClient) -> None:
    """A malformed identifier returns validation details on delete."""
    response = client.delete("/api/v1/addresses/not-a-uuid")

    assert response.status_code == 422
    assert "address_id" in _validation_fields(response.json())


def test_unhandled_error_returns_500_envelope(
    client_without_raising: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected failures return the standard envelope without details."""

    def explode(*args: object, **kwargs: object) -> list[object]:
        """Simulate a service layer crash."""
        raise RuntimeError("boom")

    monkeypatch.setattr(address_service, "list_addresses", explode)

    response = client_without_raising.get("/api/v1/addresses")

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "message": "Internal server error",
        "details": None,
    }
