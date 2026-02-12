"""UsageQuota database model for cost and token limit management."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Enum, Index, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QuotaScope(str, enum.Enum):
    """Quota scope types."""

    GLOBAL = "global"
    USER = "user"


class UsageQuota(Base):
    """Usage quota model for managing cost and token limits."""

    __tablename__ = "usage_quotas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    scope: Mapped[QuotaScope] = mapped_column(
        Enum(QuotaScope, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=QuotaScope.GLOBAL,
    )
    scope_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="User ID if scope is USER, null for GLOBAL",
    )

    # Cost limits (in USD)
    daily_cost_limit_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=True,
    )
    monthly_cost_limit_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=True,
    )

    # Token limits
    daily_token_limit: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    monthly_token_limit: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Rate limiting
    requests_per_minute: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    requests_per_hour: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Alert threshold (percentage 0-100)
    alert_threshold_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=80,
        comment="Percentage at which to trigger alerts",
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

    __table_args__ = (
        Index("idx_usage_quotas_scope", "scope"),
        Index("idx_usage_quotas_scope_id", "scope_id"),
    )

    def __repr__(self) -> str:
        return f"<UsageQuota(id={self.id}, scope={self.scope.value}, scope_id='{self.scope_id}')>"
