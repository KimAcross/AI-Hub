"""Quota API schemas for requests and responses."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.usage_quota import QuotaScope


# Request schemas
class QuotaUpdate(BaseModel):
    """Request schema for updating quota settings."""

    daily_cost_limit_usd: Optional[Decimal] = Field(
        None, ge=0, description="Daily cost limit in USD (null to remove)"
    )
    monthly_cost_limit_usd: Optional[Decimal] = Field(
        None, ge=0, description="Monthly cost limit in USD (null to remove)"
    )
    daily_token_limit: Optional[int] = Field(
        None, ge=0, description="Daily token limit (null to remove)"
    )
    monthly_token_limit: Optional[int] = Field(
        None, ge=0, description="Monthly token limit (null to remove)"
    )
    requests_per_minute: Optional[int] = Field(
        None, ge=1, description="Rate limit per minute (null to remove)"
    )
    requests_per_hour: Optional[int] = Field(
        None, ge=1, description="Rate limit per hour (null to remove)"
    )
    alert_threshold_percent: Optional[int] = Field(
        None, ge=0, le=100, description="Alert threshold percentage"
    )


# Response schemas
class QuotaResponse(BaseModel):
    """Response schema for quota settings."""

    id: UUID = Field(description="Quota's unique ID")
    scope: QuotaScope = Field(description="Quota scope (global or user)")
    scope_id: Optional[str] = Field(None, description="User ID if scope is user")
    daily_cost_limit_usd: Optional[Decimal] = Field(None, description="Daily cost limit in USD")
    monthly_cost_limit_usd: Optional[Decimal] = Field(None, description="Monthly cost limit in USD")
    daily_token_limit: Optional[int] = Field(None, description="Daily token limit")
    monthly_token_limit: Optional[int] = Field(None, description="Monthly token limit")
    requests_per_minute: Optional[int] = Field(None, description="Rate limit per minute")
    requests_per_hour: Optional[int] = Field(None, description="Rate limit per hour")
    alert_threshold_percent: int = Field(description="Alert threshold percentage")

    model_config = {"from_attributes": True}


class UsageStatusResponse(BaseModel):
    """Response schema for current usage status."""

    daily_cost_used: float = Field(description="Today's cost in USD")
    daily_cost_limit: Optional[float] = Field(None, description="Daily cost limit in USD")
    daily_cost_percent: Optional[float] = Field(None, description="Percentage of daily cost limit used")
    monthly_cost_used: float = Field(description="This month's cost in USD")
    monthly_cost_limit: Optional[float] = Field(None, description="Monthly cost limit in USD")
    monthly_cost_percent: Optional[float] = Field(None, description="Percentage of monthly cost limit used")
    daily_tokens_used: int = Field(description="Today's token usage")
    daily_token_limit: Optional[int] = Field(None, description="Daily token limit")
    daily_token_percent: Optional[float] = Field(None, description="Percentage of daily token limit used")
    monthly_tokens_used: int = Field(description="This month's token usage")
    monthly_token_limit: Optional[int] = Field(None, description="Monthly token limit")
    monthly_token_percent: Optional[float] = Field(None, description="Percentage of monthly token limit used")


class QuotaAlertResponse(BaseModel):
    """Response schema for a quota alert."""

    alert_type: str = Field(description="Type of alert: 'cost' or 'tokens'")
    period: str = Field(description="Period: 'daily' or 'monthly'")
    current_value: float = Field(description="Current usage value")
    limit_value: float = Field(description="Limit value")
    percent_used: float = Field(description="Percentage of limit used")
    threshold_percent: int = Field(description="Alert threshold percentage")
    is_exceeded: bool = Field(description="Whether the limit is exceeded")


class QuotaAlertsResponse(BaseModel):
    """Response schema for list of quota alerts."""

    alerts: list[QuotaAlertResponse] = Field(description="List of active alerts")
