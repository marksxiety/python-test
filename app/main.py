"""FastAPI application setup."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.openapi import APP_DESCRIPTION, install_openapi
from app.database.connection import create_tables
from app.v1.routes import router as v1_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Prepare logging and the database before serving requests."""
    setup_logging()
    create_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    description=APP_DESCRIPTION,
    version=settings.app_version,
    lifespan=lifespan,
)
register_exception_handlers(app)
app.include_router(v1_router, prefix="/api/v1", tags=["Addresses v1"])
install_openapi(app)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
    )
