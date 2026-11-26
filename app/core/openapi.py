"""OpenAPI metadata and schema customization."""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

APP_DESCRIPTION = (
    "Address book API with coordinate-based search.\n\n"
    "## Response format\n"
    "Every response has `success`, `message`, and `details`. Errors set "
    "`success` to `false`; validation errors list `{field, message}` "
    "objects in `details`."
)


def _restore_example_details(schema: dict[str, Any]) -> None:
    """Restore `details: null` that FastAPI strips from response examples."""
    for methods in schema.get("paths", {}).values():
        for operation in methods.values():
            for response in operation.get("responses", {}).values():
                for media in response.get("content", {}).values():
                    example = media.get("example")
                    if isinstance(example, dict) and "success" in example:
                        example.setdefault("details", None)


def install_openapi(app: FastAPI) -> None:
    """Install a schema generator that keeps null `details` in examples."""

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        _restore_example_details(schema)
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
