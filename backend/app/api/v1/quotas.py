"""Quota management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_info, get_db, require_admin_role, verify_csrf_token
from app.core.rate_limit import limiter
from app.schemas.quota import (
    QuotaAlertResponse,
    QuotaAlertsResponse,
    QuotaResponse,
    QuotaUpdate,
    UsageStatusResponse,
)
from app.services.audit_service import AuditService
from app.services.quota_service import QuotaService

router = APIRouter(prefix="/admin/quotas", tags=["Admin - Quotas"])


@router.get("/global", response_model=QuotaResponse)
@limiter.limit("30/minute")
async def get_global_quota(
    request: Request,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
) -> QuotaResponse:
    """Get global usage quota settings.

    Returns:
        Global quota configuration.
    """
    quota_service = QuotaService(db)
    quota = await quota_service.get_or_create_global_quota()
    return QuotaResponse.model_validate(quota)


@router.patch("/global", response_model=QuotaResponse)
@limiter.limit("10/minute")
async def update_global_quota(
    request: Request,
    data: QuotaUpdate,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> QuotaResponse:
    """Update global usage quota settings.

    Returns:
        Updated quota configuration.
    """
    quota_service = QuotaService(db)
    audit_service = AuditService(db)

    # Get old values for audit
    old_quota = await quota_service.get_or_create_global_quota()
    old_values = {
        "daily_cost_limit_usd": float(old_quota.daily_cost_limit_usd)
        if old_quota.daily_cost_limit_usd
        else None,
        "monthly_cost_limit_usd": float(old_quota.monthly_cost_limit_usd)
        if old_quota.monthly_cost_limit_usd
        else None,
        "daily_token_limit": old_quota.daily_token_limit,
        "monthly_token_limit": old_quota.monthly_token_limit,
        "alert_threshold_percent": old_quota.alert_threshold_percent,
    }

    quota = await quota_service.update_global_quota(
        daily_cost_limit_usd=data.daily_cost_limit_usd,
        monthly_cost_limit_usd=data.monthly_cost_limit_usd,
        daily_token_limit=data.daily_token_limit,
        monthly_token_limit=data.monthly_token_limit,
        requests_per_minute=data.requests_per_minute,
        requests_per_hour=data.requests_per_hour,
        alert_threshold_percent=data.alert_threshold_percent,
    )

    new_values = {
        "daily_cost_limit_usd": float(quota.daily_cost_limit_usd)
        if quota.daily_cost_limit_usd
        else None,
        "monthly_cost_limit_usd": float(quota.monthly_cost_limit_usd)
        if quota.monthly_cost_limit_usd
        else None,
        "daily_token_limit": quota.daily_token_limit,
        "monthly_token_limit": quota.monthly_token_limit,
        "alert_threshold_percent": quota.alert_threshold_percent,
    }

    ip, user_agent = get_client_info(request)
    await audit_service.log_quota_action(
        action="updated",
        quota_id=str(quota.id),
        actor=_admin.get("email", "admin"),
        actor_id=_admin.get("sub"),
        ip_address=ip,
        user_agent=user_agent,
        old_values=old_values,
        new_values=new_values,
    )

    await db.commit()
    return QuotaResponse.model_validate(quota)


@router.get("/usage", response_model=UsageStatusResponse)
@limiter.limit("30/minute")
async def get_usage_status(
    request: Request,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
) -> UsageStatusResponse:
    """Get current usage status with limits and percentages.

    Returns:
        Current usage compared to limits.
    """
    quota_service = QuotaService(db)
    status = await quota_service.get_usage_status()
    return UsageStatusResponse(**status)


@router.get("/alerts", response_model=QuotaAlertsResponse)
@limiter.limit("30/minute")
async def get_quota_alerts(
    request: Request,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
) -> QuotaAlertsResponse:
    """Get active quota alerts.

    Returns alerts for limits that are approaching or exceeded.

    Returns:
        List of active alerts.
    """
    quota_service = QuotaService(db)
    alerts = await quota_service.get_alerts()

    return QuotaAlertsResponse(
        alerts=[
            QuotaAlertResponse(
                alert_type=a.alert_type,
                period=a.period,
                current_value=a.current_value,
                limit_value=a.limit_value,
                percent_used=a.percent_used,
                threshold_percent=a.threshold_percent,
                is_exceeded=a.is_exceeded,
            )
            for a in alerts
        ]
    )
