"""Audit log API endpoints."""

import csv
import io
import json
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin_role
from app.core.rate_limit import limiter
from app.schemas.audit import (
    AuditLogListResponse,
    AuditLogResponse,
    AuditLogSummaryItem,
    AuditLogSummaryResponse,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin/audit", tags=["Admin - Audit"])


@router.get("", response_model=AuditLogListResponse)
@limiter.limit("30/minute")
async def query_audit_logs(
    request: Request,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
    action: Optional[str] = Query(
        None, description="Filter by action (or action prefix)"
    ),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    actor: Optional[str] = Query(None, description="Filter by actor"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> AuditLogListResponse:
    """Query audit logs with filters.

    Returns:
        Paginated list of audit log entries.
    """
    audit_service = AuditService(db)

    logs, total = await audit_service.query(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        actor=actor,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/recent", response_model=list[AuditLogResponse])
@limiter.limit("30/minute")
async def get_recent_audit_logs(
    request: Request,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
) -> list[AuditLogResponse]:
    """Get recent audit log entries.

    Returns:
        List of recent audit log entries.
    """
    audit_service = AuditService(db)
    logs = await audit_service.get_recent(limit)
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/summary", response_model=AuditLogSummaryResponse)
@limiter.limit("30/minute")
async def get_audit_summary(
    request: Request,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=90, description="Number of days to summarize"),
) -> AuditLogSummaryResponse:
    """Get summary of audit actions by type.

    Returns:
        Action counts for the period.
    """
    audit_service = AuditService(db)
    summary = await audit_service.get_action_summary(days)

    return AuditLogSummaryResponse(
        summary=[AuditLogSummaryItem(**item) for item in summary],
        period_days=days,
    )


@router.get("/export")
@limiter.limit("10/minute")
async def export_audit_logs(
    request: Request,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
    format: str = Query("csv", description="Export format (csv or json)"),
    action: Optional[str] = Query(None, description="Filter by action"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum results"),
) -> StreamingResponse:
    """Export audit logs as CSV or JSON.

    Returns:
        Streaming file download.
    """
    audit_service = AuditService(db)

    logs, _ = await audit_service.query(
        action=action,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=0,
    )

    if format == "json":
        data = [
            {
                "id": str(log.id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "actor": log.actor,
                "actor_id": log.actor_id,
                "ip_address": log.ip_address,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
        content = json.dumps(data, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=audit-logs.json"},
        )

    # CSV export
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "action",
            "resource_type",
            "resource_id",
            "actor",
            "actor_id",
            "ip_address",
            "details",
            "created_at",
        ]
    )
    for log in logs:
        writer.writerow(
            [
                str(log.id),
                log.action,
                log.resource_type,
                log.resource_id,
                log.actor,
                log.actor_id,
                log.ip_address,
                json.dumps(log.details) if log.details else "",
                log.created_at.isoformat() if log.created_at else "",
            ]
        )

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-logs.csv"},
    )
