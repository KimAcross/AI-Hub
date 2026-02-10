"""Settings schemas for API requests and responses."""

from typing import Literal
from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    """Response schema for settings."""

    openrouter_api_key_set: bool = Field(
        description="Whether an OpenRouter API key is configured"
    )
    default_model: str = Field(description="Default model for new conversations")
    embedding_model: str = Field(description="Model used for embeddings")
    max_file_size_mb: int = Field(description="Maximum file upload size in MB")
    language: str = Field(description="Preferred language for the interface")
    streaming_enabled: bool = Field(description="Whether streaming responses are enabled")
    auto_save_interval: int = Field(description="Auto-save interval in seconds (0 to disable)")


class SettingsUpdate(BaseModel):
    """Request schema for updating settings."""

    openrouter_api_key: str | None = Field(
        default=None, description="OpenRouter API key (set to empty string to clear)"
    )
    default_model: str | None = Field(
        default=None, description="Default model for new conversations"
    )
    language: str | None = Field(
        default=None, description="Preferred language for the interface"
    )
    streaming_enabled: bool | None = Field(
        default=None, description="Whether streaming responses are enabled"
    )
    auto_save_interval: int | None = Field(
        default=None, ge=0, le=300, description="Auto-save interval in seconds (0-300, 0 to disable)"
    )
