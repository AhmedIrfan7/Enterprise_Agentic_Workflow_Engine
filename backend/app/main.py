import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database import init_db
from app.utils.logging import configure_logging
from app.api.v1.router import api_router

settings = get_settings()
configure_logging(debug=settings.DEBUG)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Enterprise Agentic Workflow Engine...")
    await init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Database and storage initialized.")
    yield
    logger.info("Shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-grade AI agentic workflow orchestration platform.",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Register routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # WebSocket endpoint lives at root level (no /api/v1 prefix) to support direct ws:// connections
    from app.api.v1.endpoints.websocket import router as ws_router
    app.include_router(ws_router)

    # Global exception handlers
    _register_exception_handlers(app)

    return app


def _register_exception_handlers(app: FastAPI) -> None:
    from app.utils.exceptions import (
        AppException,
        app_exception_handler,
        validation_exception_handler,
        unhandled_exception_handler,
    )
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


app = create_app()
