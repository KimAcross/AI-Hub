"""FastAPI application entry point."""

import asyncio
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
    generate_request_id,
    get_logger,
    request_id_var,
    setup_logging,
    user_id_var,
)
from app.core.rate_limit import get_limiter, rate_limit_exceeded_handler

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup — configure logging first
    setup_logging(log_level=settings.log_level, log_format=settings.log_format)
    logger.info(f"Starting {settings.app_name} in {settings.app_env} mode...")
    if settings.is_production:
        logger.info("Production mode: API docs disabled, strict CORS enabled")

    # Start ingestion reaper background task
    from app.services.ingestion_reaper import get_ingestion_reaper

    reaper = get_ingestion_reaper()
    reaper_task = asyncio.create_task(reaper.run())

    yield

    # Shutdown
    reaper.stop()
    reaper_task.cancel()
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


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Inject request_id and user context into every request for log correlation."""

    async def dispatch(self, request: Request, call_next):
        rid = generate_request_id()
        request_id_var.set(rid)

        # Extract user_id from Authorization header (JWT) if present
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from jose import jwt

                token = auth_header[7:]
                payload = jwt.decode(
                    token, settings.secret_key, algorithms=["HS256"],
                    options={"verify_exp": False},
                )
                if sub := payload.get("sub"):
                    user_id_var.set(str(sub))
            except Exception:
                pass

        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
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


app.add_middleware(RequestContextMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


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
