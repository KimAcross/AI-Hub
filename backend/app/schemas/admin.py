"""Admin API schemas for requests and responses."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


# Auth schemas
class AdminLoginRequest(BaseModel):
    """Request schema for admin login."""

    password: str = Field(..., min_length=1, description="Admin password")


class AdminLoginResponse(BaseModel):
    """Response schema for admin login."""

    token: str = Field(description="JWT session token for authentication")
    expires_at: datetime = Field(description="Token expiration timestamp")
    csrf_token: str = Field(description="CSRF token for state-changing requests")


class AdminVerifyResponse(BaseModel):
    """Response schema for token verification."""

    valid: bool = Field(description="Whether the token is valid")


# Usage schemas
class UsageSummaryResponse(BaseModel):
    """Response schema for usage summary."""

    total_tokens: int = Field(description="Total tokens used")
    total_prompt_tokens: int = Field(description="Total prompt tokens used")
    total_completion_tokens: int = Field(description="Total completion tokens used")
    total_cost_usd: Decimal = Field(description="Total cost in USD")
    total_conversations: int = Field(description="Number of unique conversations")
    total_messages: int = Field(description="Total number of messages")
    period_start: datetime = Field(description="Start of the reporting period")
    period_end: datetime = Field(description="End of the reporting period")


class UsageByModel(BaseModel):
    """Usage breakdown by model."""

    model: str = Field(description="Model ID")
    total_tokens: int = Field(description="Total tokens used with this model")
    prompt_tokens: int = Field(description="Prompt tokens used")
    completion_tokens: int = Field(description="Completion tokens used")
    cost_usd: Decimal = Field(description="Cost in USD")
    message_count: int = Field(description="Number of messages")


class UsageByAssistant(BaseModel):
    """Usage breakdown by assistant."""

    assistant_id: Optional[str] = Field(description="Assistant ID (null if deleted)")
    assistant_name: Optional[str] = Field(description="Assistant name")
    total_tokens: int = Field(description="Total tokens used")
    prompt_tokens: int = Field(description="Prompt tokens used")
    completion_tokens: int = Field(description="Completion tokens used")
    cost_usd: Decimal = Field(description="Cost in USD")
    message_count: int = Field(description="Number of messages")


class UsageBreakdownResponse(BaseModel):
    """Response schema for usage breakdown."""

    by_model: list[UsageByModel] = Field(description="Usage breakdown by model")
    by_assistant: list[UsageByAssistant] = Field(description="Usage breakdown by assistant")


class DailyUsage(BaseModel):
    """Daily usage data point."""

    date: str = Field(description="Date in YYYY-MM-DD format")
    total_tokens: int = Field(description="Total tokens used")
    prompt_tokens: int = Field(description="Prompt tokens used")
    completion_tokens: int = Field(description="Completion tokens used")
    cost_usd: Decimal = Field(description="Cost in USD")
    message_count: int = Field(description="Number of messages")


class DailyUsageResponse(BaseModel):
    """Response schema for daily usage."""

    data: list[DailyUsage] = Field(description="Daily usage data points")
    days: int = Field(description="Number of days in the response")


# Health schemas
class ComponentHealth(BaseModel):
    """Health status of a single component."""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        description="Component health status"
    )
    latency_ms: Optional[int] = Field(
        default=None, description="Response latency in milliseconds"
    )
    error: Optional[str] = Field(default=None, description="Error message if unhealthy")


class SystemHealthResponse(BaseModel):
    """Response schema for system health."""

    database: ComponentHealth = Field(description="Database health status")
    openrouter: ComponentHealth = Field(description="OpenRouter API health status")
    chromadb: ComponentHealth = Field(description="ChromaDB health status")
    api_key_configured: bool = Field(description="Whether API key is configured")
    api_key_masked: Optional[str] = Field(
        default=None, description="Masked API key (first/last 4 chars)"
    )
