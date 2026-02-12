"""APIKey database model for multi-provider AI API key management."""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class APIKeyProvider(str, enum.Enum):
    """Supported AI provider types."""

    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    CUSTOM = "custom"


class APIKeyStatus(str, enum.Enum):
    """API key test status."""

    VALID = "valid"
    INVALID = "invalid"
    UNTESTED = "untested"


class APIKey(Base):
    """API key model for storing multiple provider API keys."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    provider: Mapped[APIKeyProvider] = mapped_column(
        Enum(APIKeyProvider, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_key: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Fernet-encrypted API key",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Default key for this provider",
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_tested_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    test_status: Mapped[APIKeyStatus] = mapped_column(
        Enum(APIKeyStatus, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=APIKeyStatus.UNTESTED,
    )
    test_error: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Error message from last test if failed",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    rotated_from_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="Reference to previous key if this was rotated",
    )

    __table_args__ = (
        Index("idx_api_keys_provider", "provider"),
        Index("idx_api_keys_is_active", "is_active"),
        Index("idx_api_keys_is_default", "is_default"),
    )

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, provider={self.provider.value}, name='{self.name}')>"
