"""Admin API endpoints for usage tracking and system health."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, verify_admin_token
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.schemas.admin import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminVerifyResponse,
    ComponentHealth,
    DailyUsage,
    DailyUsageResponse,
    SystemHealthResponse,
    UsageBreakdownResponse,
    UsageByAssistant,
    UsageByModel,
    UsageSummaryResponse,
)
from app.services.admin_auth_service import get_admin_auth_service
from app.services.settings_service import SettingsService
from app.services.usage_log_service import UsageLogService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=AdminLoginResponse)
@limiter.limit("5/minute")
async def admin_login(
    request: Request, login_request: AdminLoginRequest
) -> AdminLoginResponse:
    """Login to admin dashboard.

    Args:
        request: FastAPI request (required for rate limiting).
        login_request: Login request with password.

    Returns:
        Token and expiration time.

    Raises:
        HTTPException: If password is invalid or admin not configured.
    """
    auth_service = get_admin_auth_service()

    if not auth_service.admin_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access not configured. Set ADMIN_PASSWORD environment variable.",
        )

    if not auth_service.verify_admin_password(login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    token, expires_at, csrf_token = auth_service.generate_token()

    return AdminLoginResponse(token=token, expires_at=expires_at, csrf_token=csrf_token)


@router.get("/verify", response_model=AdminVerifyResponse)
async def verify_token(
    _: Annotated[bool, Depends(verify_admin_token)],
) -> AdminVerifyResponse:
    """Verify if the admin token is valid.

    Returns:
        Verification result.
    """
    return AdminVerifyResponse(valid=True)


@router.get("/usage/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    _: Annotated[bool, Depends(verify_admin_token)],
    db: AsyncSession = Depends(get_db),
) -> UsageSummaryResponse:
    """Get usage summary for the last 30 days.

    Returns:
        Total tokens, cost, and message counts.
    """
    service = UsageLogService(db)
    summary = await service.get_summary()

    return UsageSummaryResponse(**summary)


@router.get("/usage/breakdown", response_model=UsageBreakdownResponse)
async def get_usage_breakdown(
    _: Annotated[bool, Depends(verify_admin_token)],
    db: AsyncSession = Depends(get_db),
) -> UsageBreakdownResponse:
    """Get usage breakdown by model and assistant.

    Returns:
        Usage stats grouped by model and assistant.
    """
    service = UsageLogService(db)

    by_model_data = await service.get_breakdown_by_model()
    by_assistant_data = await service.get_breakdown_by_assistant()

    by_model = [UsageByModel(**item) for item in by_model_data]
    by_assistant = [UsageByAssistant(**item) for item in by_assistant_data]

    return UsageBreakdownResponse(by_model=by_model, by_assistant=by_assistant)


@router.get("/usage/daily", response_model=DailyUsageResponse)
async def get_daily_usage(
    _: Annotated[bool, Depends(verify_admin_token)],
    db: AsyncSession = Depends(get_db),
    days: int = 30,
) -> DailyUsageResponse:
    """Get daily usage for the last N days.

    Args:
        days: Number of days to retrieve (default 30, max 90).

    Returns:
        Daily usage data points.
    """
    days = min(max(days, 1), 90)  # Clamp between 1 and 90

    service = UsageLogService(db)
    daily_data = await service.get_daily_usage(days)

    data = [DailyUsage(**item) for item in daily_data]

    return DailyUsageResponse(data=data, days=days)


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    _: Annotated[bool, Depends(verify_admin_token)],
    db: AsyncSession = Depends(get_db),
) -> SystemHealthResponse:
    """Get comprehensive system health status.

    Returns:
        Health status for all system components.
    """
    settings = get_settings()
    settings_service = SettingsService(db)

    # Check Database
    db_health = await _check_database(db)

    # Check OpenRouter
    openrouter_health = await _check_openrouter()

    # Check ChromaDB
    chromadb_health = _check_chromadb()

    # Check API key status
    api_key = (
        await settings_service.get_openrouter_api_key() or settings.openrouter_api_key
    )
    api_key_configured = bool(api_key)
    api_key_masked = _mask_api_key(api_key) if api_key else None

    return SystemHealthResponse(
        database=db_health,
        openrouter=openrouter_health,
        chromadb=chromadb_health,
        api_key_configured=api_key_configured,
        api_key_masked=api_key_masked,
    )


async def _check_database(db: AsyncSession) -> ComponentHealth:
    """Check database connectivity."""
    try:
        start = time.time()
        await db.execute(text("SELECT 1"))
        latency = int((time.time() - start) * 1000)
        return ComponentHealth(status="healthy", latency_ms=latency)
    except Exception as e:
        return ComponentHealth(status="unhealthy", error=str(e))


async def _check_openrouter() -> ComponentHealth:
    """Check OpenRouter API connectivity."""
    from app.services.openrouter_service import get_openrouter_service

    try:
        service = get_openrouter_service()
        is_connected, latency_ms, error = await service.check_connectivity()

        if is_connected:
            return ComponentHealth(status="healthy", latency_ms=latency_ms)
        elif error and "Invalid API key" in error:
            return ComponentHealth(
                status="degraded", latency_ms=latency_ms, error=error
            )
        else:
            return ComponentHealth(status="unhealthy", error=error)

    except Exception as e:
        return ComponentHealth(status="unhealthy", error=str(e))


def _check_chromadb() -> ComponentHealth:
    """Check ChromaDB connectivity."""
    try:
        start = time.time()

        from app.services.chroma_service import ChromaService

        chroma = ChromaService()
        chroma.client.heartbeat()

        latency = int((time.time() - start) * 1000)
        return ComponentHealth(status="healthy", latency_ms=latency)
    except Exception as e:
        return ComponentHealth(status="unhealthy", error=str(e))


def _mask_api_key(key: str) -> str:
    """Mask API key showing only first/last 4 chars."""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}...{key[-4:]}"
