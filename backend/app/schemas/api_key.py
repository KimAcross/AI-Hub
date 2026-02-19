"""API Key schemas for requests and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.api_key import APIKeyProvider, APIKeyStatus


# Request schemas
class APIKeyCreate(BaseModel):
    """Request schema for creating an API key."""

    provider: APIKeyProvider = Field(..., description="AI provider type")
    name: str = Field(
        ..., min_length=1, max_length=100, description="Display name for the key"
    )
    api_key: str = Field(..., min_length=1, description="The API key value")
    is_default: bool = Field(
        default=False, description="Set as default for this provider"
    )


class APIKeyUpdate(BaseModel):
    """Request schema for updating an API key."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="New display name"
    )
    is_active: Optional[bool] = Field(None, description="Active status")


class APIKeyRotate(BaseModel):
    """Request schema for rotating an API key."""

    new_api_key: str = Field(..., min_length=1, description="New API key value")


# Response schemas
class APIKeyResponse(BaseModel):
    """Response schema for an API key."""

    id: UUID = Field(description="API key's unique ID")
    provider: APIKeyProvider = Field(description="AI provider type")
    name: str = Field(description="Display name")
    key_masked: str = Field(description="Masked key (first/last 4 chars)")
    is_active: bool = Field(description="Whether the key is active")
    is_default: bool = Field(
        description="Whether this is the default key for the provider"
    )
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    last_tested_at: Optional[datetime] = Field(None, description="Last test timestamp")
    test_status: APIKeyStatus = Field(description="Last test result status")
    test_error: Optional[str] = Field(
        None, description="Error from last test if failed"
    )
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    model_config = {"from_attributes": True}


class APIKeyTestResponse(BaseModel):
    """Response schema for API key test."""

    valid: bool = Field(description="Whether the key is valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    latency_ms: Optional[int] = Field(None, description="Test latency in milliseconds")


class APIKeyListResponse(BaseModel):
    """Response schema for list of API keys."""

    keys: list[APIKeyResponse] = Field(description="List of API keys")
    total: int = Field(description="Total number of keys")
