"""Audit log API schemas for requests and responses."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Response schemas
class AuditLogResponse(BaseModel):
    """Response schema for an audit log entry."""

    id: UUID = Field(description="Audit log entry ID")
    action: str = Field(description="Action performed")
    resource_type: str = Field(description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of the affected resource")
    actor: str = Field(description="Actor who performed the action")
    actor_id: Optional[str] = Field(None, description="Actor's user ID")
    ip_address: Optional[str] = Field(None, description="Request IP address")
    user_agent: Optional[str] = Field(None, description="Request user agent")
    details: Optional[dict[str, Any]] = Field(None, description="Additional action details")
    old_values: Optional[dict[str, Any]] = Field(None, description="Previous values")
    new_values: Optional[dict[str, Any]] = Field(None, description="New values")
    created_at: datetime = Field(description="Timestamp when action occurred")

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Response schema for paginated audit log list."""

    items: list[AuditLogResponse] = Field(description="List of audit log entries")
    total: int = Field(description="Total number of entries matching filters")
    limit: int = Field(description="Maximum entries returned")
    offset: int = Field(description="Offset from start")


class AuditLogSummaryItem(BaseModel):
    """Summary item for action counts."""

    action: str = Field(description="Action type")
    count: int = Field(description="Number of occurrences")


class AuditLogSummaryResponse(BaseModel):
    """Response schema for audit log summary."""

    summary: list[AuditLogSummaryItem] = Field(description="Action count summary")
    period_days: int = Field(description="Number of days covered")
