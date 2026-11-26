# Address Book API

## Overview

Address Book API lets users create, update, delete, and retrieve addresses with validated geographic coordinates. It stores addresses in SQLite and supports distance-based searches using latitude and longitude.

## Setup

Follow these steps from a fresh checkout. Python 3.11 or newer is required, and
every command below should be run from the repository root.

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Activate it. On macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

   On Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the pinned dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   This file includes both runtime dependencies and test tools.

4. Create the local environment file:

   ```bash
   cp .env.example .env
   ```

   In PowerShell, use `Copy-Item .env.example .env`.

## Database

5. (Optional) Initialize the SQLite database explicitly:

   ```bash
   python -m scripts.init_db
   ```

   The app creates the `addresses` table on startup when it is missing, so this
   step is only needed for explicit setup (for example, in a deployment or CI
   pipeline). With the default settings, the database file is `address_book.db`
   in the project root; delete it to reset the database. There are no migrations
   and no seed data.

## Run

6. Start the API:

   ```bash
   python -m app.main
   ```

   The server uses `API_HOST` and `API_PORT` from `.env`, defaulting to `127.0.0.1:8000`. Swagger is available at `/docs`; every implemented route can be tried there without extra tools.

## Routes

Default base URL (`API_HOST` and `API_PORT`): `http://127.0.0.1:8000`  
API prefix: `/api/v1`.

| Method | Path | Description | Success status |
|---|---|---|---:|
| POST | `/addresses` | Create an address | 201 |
| GET | `/addresses` | List addresses | 200 |
| GET | `/addresses/nearby` | Find nearby addresses | 200 |
| GET | `/addresses/{address_id}` | Get one address | 200 |
| PATCH | `/addresses/{address_id}` | Partially update an address | 200 |
| DELETE | `/addresses/{address_id}` | Delete an address | 200 |

Every API response uses the shared `success`, `message`, and `details` envelope.
See [ROUTES.md](ROUTES.md) for sample payloads and expected responses.

## Logging

Logging is centralized in `app/core/logging.py`:

```python
print_logging("info", "Application started")
```

`setup_logging()` configures the console and a rotating `LOG_DIR/app.log`
(5 MB per file, 5 backups). `LOG_LEVEL` controls verbosity (default `INFO`).
Application lines include the calling module and line number.

## Libraries used

### fastapi
The core requirement of the project. Beyond that, it cuts down boilerplate with native async support and auto-generated OpenAPI docs, letting me focus on the actual business logic instead of wiring up basic routing and documentation.

### uvicorn[standard]
Running the app via `fastapi` CLI arguments works, but invoking `uvicorn` directly gives me explicit control over the ASGI server—using `--reload` for fast feedback during local development, and taking advantage of the `[standard]` extras (`uvloop` and `httptools`) for better runtime performance.

### sqlalchemy
I prefer using this for readability and maintainability by maximizing the ORM for standard operations. At the same time, it doesn't box me in—when a use case gets too complex or needs specific database tuning, I can use `text()` to execute raw SQL cleanly without abandoning the rest of the setup.

### pydantic
Enforces strict data contracts at the entry point of the app. Instead of writing manual validation checks everywhere, it validates and parses incoming payloads automatically so bad data fails fast before it ever hits the business logic or database.

### pydantic-settings
Keeps environment configuration clean and type-safe. Instead of scattering `os.getenv()` calls across the codebase and risking silent `None` bugs at runtime, it loads `.env` values into a single validated config object—if a required variable is missing, the app fails immediately on startup.

### pytest
Much cleaner and less verbose than Python's built-in `unittest`. Fixtures make it straightforward to set up and tear down test states (like isolated DB sessions), which keeps the test suite readable and actually maintainable.

### httpx2
Used only by the unit tests, under the hood of FastAPI's `TestClient`, to send real HTTP requests to the API endpoints through the app without spinning up a live server. It is a test dependency, not part of the running application.

## Running tests

```bash
pytest
```

The `tests/` folder mirrors the `app/` structure.


## Notes and next steps

This API is intentionally kept simple and scoped to the requirements. The following were considered and left out on purpose, and each can be added without restructuring the project.

- **Authentication:** out of scope. Next step would be an API key or JWT dependency applied at the router level.
- **Rate limiting:** not needed at this stage. It would normally sit at the reverse proxy or API gateway once the API is exposed publicly, or use `slowapi` if it has to live in the app.
- **Idempotency:** `POST /addresses` is not idempotent, so a retried request creates a duplicate. An `Idempotency-Key` header backed by a small table would be the next step if clients need safe retries. GET, PATCH, and DELETE are already safe to retry.
- **Audit trail:** only `created_at` and `updated_at` are tracked. An `audit_logs` table would be the next step for full change history.
- **Migrations:** tables are created with `create_all()` on startup, so changing a column means recreating the database. Alembic would be the next step once the schema starts changing.
- **Versioning:** a `v2/` router can be added for breaking changes without touching `v1/`.