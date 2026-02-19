"""FastAPI application entry point."""

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AIAcrossException
from app.core.logging import (
    clear_request_context,
    configure_logging,
    set_request_context,
)
from app.core.rate_limit import get_limiter, rate_limit_exceeded_handler
from app.db.session import async_session_maker
from app.services.ingestion_reaper import IngestionReaper
from app.services.admin_auth_service import get_admin_auth_service

from jose import JWTError, jwt

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.app_env} mode...")
    if settings.is_production:
        logger.info("Production mode: API docs disabled, strict CORS enabled")
    reaper_task = None
    if settings.app_env.lower() != "testing":
        reaper_task = asyncio.create_task(run_ingestion_reaper_loop())
    yield
    # Shutdown
    if reaper_task:
        reaper_task.cancel()
        try:
            await reaper_task
        except asyncio.CancelledError:
            logger.info("Ingestion reaper stopped")
    logger.info(f"Shutting down {settings.app_name}...")


# Disable docs in production
docs_url = "/docs" if settings.debug or not settings.is_production else None
redoc_url = "/redoc" if settings.debug or not settings.is_production else None
openapi_url = "/openapi.json" if docs_url else None

app = FastAPI(
    title=settings.app_name,
    description="AI content platform for creating and managing specialized AI assistants",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

# Add rate limiter to app state
if settings.rate_limit_enabled:
    limiter = get_limiter()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configure CORS - hardened for production
if settings.is_production:
    # Production: explicit methods and headers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Admin-Token",
            "X-CSRF-Token",
        ],
        max_age=86400,  # Cache preflight for 24 hours
    )
else:
    # Development: permissive for easier debugging
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self' https://openrouter.ai"
        )
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response


def _extract_user_id_from_token(request: Request) -> str | None:
    """Best-effort extraction of user_id from authentication token."""
    token = request.headers.get("X-Admin-Token")
    if not token:
        return None

    admin_payload = get_admin_auth_service().verify_token(token)
    if admin_payload:
        sub = admin_payload.get("sub")
        return None if sub == "admin" else str(sub)

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        return None

    sub = payload.get("sub")
    return str(sub) if sub else None


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Inject per-request correlation context and response headers."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        user_id = _extract_user_id_from_token(request)

        set_request_context(request_id=request_id, user_id=user_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            clear_request_context()


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)


async def run_ingestion_reaper_loop() -> None:
    """Run periodic ingestion recovery in a background task."""
    await asyncio.sleep(2)
    while True:
        try:
            async with async_session_maker() as session:
                reaper = IngestionReaper(session)
                await reaper.run_once()
                await session.commit()
        except Exception:
            logger.exception("Ingestion reaper iteration failed")
        await asyncio.sleep(settings.ingestion_reaper_interval_seconds)


@app.exception_handler(AIAcrossException)
async def aiacross_exception_handler(
    request: Request,
    exc: AIAcrossException,
) -> JSONResponse:
    """Handle custom AI-Across exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
        },
    )


# Include API routes
app.include_router(api_router)


@app.get("/", tags=["health"])
async def root():
    """Root endpoint returning API info."""
    response = {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
    }
    # Only include docs URL if docs are enabled
    if docs_url:
        response["docs"] = docs_url
    return response


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
