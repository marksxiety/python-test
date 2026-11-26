Request and response examples for routes currently implemented by the Address Book API.

Default base URL (`API_HOST` and `API_PORT`): `http://127.0.0.1:8000`

API prefix: `/api/v1`

Interactive documentation is also available at `/docs`.

Every JSON response uses the same envelope:

| Field | Type | Description |
|---|---|---|
| `success` | boolean | `true` for successful requests, `false` for errors |
| `message` | string | Human-readable result message |
| `details` | object, array, or null | Response payload, or error details |

Successful create requests return `201`; all other successful requests return
`200`. Validation failures return `422`, missing resources return `404`, and
unexpected failures return `500`. Error responses other than validation set
`details` to `null`; validation errors return a list of `{field, message}`
objects.

### Create address

`POST /api/v1/addresses`

**Headers**

| Key | Value |
|---|---|
| Content-Type | application/json |

**Body**

```json
{
  "name": "Home",
  "street": "123 Rizal St",
  "city": "Calauan",
  "province": "Laguna",
  "postal_code": "4012",
  "country": "Philippines",
  "coordinates": {
    "latitude": 14.1472,
    "longitude": 121.3167
  }
}
```

**Response: 201 Created**

```json
{
  "success": true,
  "message": "Address created",
  "details": {
    "name": "Home",
    "street": "123 Rizal St",
    "city": "Calauan",
    "province": "Laguna",
    "postal_code": "4012",
    "country": "Philippines",
    "coordinates": {
      "latitude": 14.1472,
      "longitude": 121.3167
    },
    "id": "3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f",
    "created_at": "2026-11-26T10:30:00",
    "updated_at": "2026-11-26T10:30:00"
  }
}
```

**Errors**

| Status | When |
|---|---|
| 422 | Request fields or coordinates fail validation |

```json
{
  "success": false,
  "message": "Validation failed",
  "details": [
    {
      "field": "coordinates.latitude",
      "message": "Input should be less than or equal to 90"
    }
  ]
}
```

Multiple validation errors produce one `{field, message}` object per error in
`details`.

### List addresses

`GET /api/v1/addresses`

**Query params**

| Param | Required | Example | Rule |
|---|---|---:|---|
| skip | No | 0 | Must be at least 0; defaults to 0 |
| limit | No | 50 | Must be 1-100; defaults to 50 |

Example URL: `http://127.0.0.1:8000/api/v1/addresses?skip=0&limit=50`

**Response: 200 OK**

```json
{
  "success": true,
  "message": "Addresses retrieved",
  "details": [
    {
      "name": "Home",
      "street": "123 Rizal St",
      "city": "Calauan",
      "province": "Laguna",
      "postal_code": "4012",
      "country": "Philippines",
      "coordinates": {
        "latitude": 14.1472,
        "longitude": 121.3167
      },
      "id": "3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f",
      "created_at": "2026-11-26T10:30:00",
      "updated_at": "2026-11-26T10:30:00"
    }
  ]
}
```

An empty page returns `"details": []`.

**Errors**

| Status | When |
|---|---|
| 422 | `skip` or `limit` is outside the allowed range or is not an integer |

```json
{
  "success": false,
  "message": "Validation failed",
  "details": [
    {
      "field": "limit",
      "message": "Input should be less than or equal to 100"
    }
  ]
}
```

### Find nearby addresses

`GET /api/v1/addresses/nearby`

**Query params**

| Param | Required | Example | Rule |
|---|---|---:|---|
| latitude | Yes | 14.1472 | Must be between -90 and 90 |
| longitude | Yes | 121.3167 | Must be between -180 and 180 |
| distance_km | Yes | 10 | Must be greater than 0 and at most 20015 |

Example URL: `http://127.0.0.1:8000/api/v1/addresses/nearby?latitude=14.1472&longitude=121.3167&distance_km=10`

Results are returned in `details`, ordered by distance (nearest first). The
calculated distance is not included in each address object.

**Response: 200 OK**

```json
{
  "success": true,
  "message": "Nearby addresses retrieved",
  "details": [
    {
      "name": "Home",
      "street": "123 Rizal St",
      "city": "Calauan",
      "province": "Laguna",
      "postal_code": "4012",
      "country": "Philippines",
      "coordinates": {
        "latitude": 14.1472,
        "longitude": 121.3167
      },
      "id": "3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f",
      "created_at": "2026-11-26T10:30:00",
      "updated_at": "2026-11-26T10:30:00"
    },
    {
      "name": "Nearby Address",
      "street": "45 Lakeview Rd",
      "city": "Calauan",
      "province": "Laguna",
      "postal_code": "4012",
      "country": "Philippines",
      "coordinates": {
        "latitude": 14.148,
        "longitude": 121.3172
      },
      "id": "00000000-0000-0000-0000-000000000002",
      "created_at": "2026-11-26T10:31:00",
      "updated_at": "2026-11-26T10:31:00"
    }
  ]
}
```

**Errors**

| Status | When |
|---|---|
| 422 | Coordinates or distance are outside the allowed range or cannot be parsed |

```json
{
  "success": false,
  "message": "Validation failed",
  "details": [
    {
      "field": "latitude",
      "message": "Input should be less than or equal to 90"
    }
  ]
}
```

### Get one address

`GET /api/v1/addresses/{address_id}`

**Path params**

| Param | Example | Rule |
|---|---|---|
| address_id | `3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f` | Must be a UUID |

**Response: 200 OK**

```json
{
  "success": true,
  "message": "Address retrieved",
  "details": {
    "name": "Home",
    "street": "123 Rizal St",
    "city": "Calauan",
    "province": "Laguna",
    "postal_code": "4012",
    "country": "Philippines",
    "coordinates": {
      "latitude": 14.1472,
      "longitude": 121.3167
    },
    "id": "3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f",
    "created_at": "2026-11-26T10:30:00",
    "updated_at": "2026-11-26T10:30:00"
  }
}
```

**Errors**

| Status | When |
|---|---|
| 404 | No address has the supplied UUID |
| 422 | `address_id` is not a valid UUID |

404 response:

```json
{
  "success": false,
  "message": "Address 3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f not found",
  "details": null
}
```

422 response for a malformed UUID:

```json
{
  "success": false,
  "message": "Validation failed",
  "details": [
    {
      "field": "address_id",
      "message": "Input should be a valid UUID"
    }
  ]
}
```

The actual Pydantic message also includes the parser detail, such as the invalid
character and position.

### Update address

`PATCH /api/v1/addresses/{address_id}`

**Path params**

| Param | Example | Rule |
|---|---|---|
| address_id | `3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f` | Must be a UUID |

**Headers**

| Key | Value |
|---|---|
| Content-Type | application/json |

**Body**

```json
{
  "city": "Calauan"
}
```

Only the fields sent in the body are changed; omitted fields remain unchanged.
`postal_code` can be cleared by sending `null`. Sending `null` for any other
field returns `422`.

**Response: 200 OK**

```json
{
  "success": true,
  "message": "Address updated",
  "details": {
    "name": "Home",
    "street": "123 Rizal St",
    "city": "Calauan",
    "province": "Laguna",
    "postal_code": "4012",
    "country": "Philippines",
    "coordinates": {
      "latitude": 14.1472,
      "longitude": 121.3167
    },
    "id": "3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f",
    "created_at": "2026-11-26T10:30:00",
    "updated_at": "2026-11-26T10:30:00"
  }
}
```

**Errors**

| Status | When |
|---|---|
| 404 | No address has the supplied UUID |
| 422 | `address_id` or an update field fails validation |

404 response:

```json
{
  "success": false,
  "message": "Address 3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f not found",
  "details": null
}
```

### Delete address

`DELETE /api/v1/addresses/{address_id}`

**Path params**

| Param | Example | Rule |
|---|---|---|
| address_id | `3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f` | Must be a UUID |

**Response: 200 OK**

```json
{
  "success": true,
  "message": "Address deleted",
  "details": null
}
```

**Errors**

| Status | When |
|---|---|
| 404 | No address has the supplied UUID |
| 422 | `address_id` is not a valid UUID |

404 response:

```json
{
  "success": false,
  "message": "Address 3f1c2d4e-8a1b-4c3d-9e2f-1a2b3c4d5e6f not found",
  "details": null
}
```

### Unexpected errors

Any unhandled failure returns `500` without exposing internal details.

```json
{
  "success": false,
  "message": "Internal server error",
  "details": null
}
```
