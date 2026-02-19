"""AuditLog database model for tracking administrative actions."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

JSON_FIELD = JSON().with_variant(JSONB, "postgresql")


class AuditLog(Base):
    """Audit log model for recording all administrative actions."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Action performed: user.created, api_key.rotated, quota.updated, etc.",
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of resource: user, api_key, quota, settings",
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="ID of the affected resource",
    )
    actor: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="system",
        comment="User email or 'system' for automated actions",
    )
    actor_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="User ID of the actor if applicable",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IPv4 or IPv6 address",
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    details: Mapped[Optional[dict]] = mapped_column(
        JSON_FIELD,
        nullable=True,
        comment="Additional context about the action",
    )
    old_values: Mapped[Optional[dict]] = mapped_column(
        JSON_FIELD,
        nullable=True,
        comment="Previous values before change",
    )
    new_values: Mapped[Optional[dict]] = mapped_column(
        JSON_FIELD,
        nullable=True,
        comment="New values after change",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource_type", "resource_type"),
        Index("idx_audit_logs_resource_id", "resource_id"),
        Index("idx_audit_logs_actor", "actor"),
        Index("idx_audit_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"
