"""Quota service for usage limits and enforcement."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage_log import UsageLog
from app.models.usage_quota import QuotaScope, UsageQuota


@dataclass
class QuotaCheckResult:
    """Result of a quota check."""

    allowed: bool
    reason: Optional[str] = None
    daily_cost_used: Decimal = Decimal("0")
    daily_cost_limit: Optional[Decimal] = None
    monthly_cost_used: Decimal = Decimal("0")
    monthly_cost_limit: Optional[Decimal] = None
    daily_tokens_used: int = 0
    daily_token_limit: Optional[int] = None
    monthly_tokens_used: int = 0
    monthly_token_limit: Optional[int] = None


@dataclass
class QuotaAlert:
    """Alert when approaching or exceeding limits."""

    alert_type: str  # "cost" or "tokens"
    period: str  # "daily" or "monthly"
    current_value: float
    limit_value: float
    percent_used: float
    threshold_percent: int
    is_exceeded: bool


class QuotaService:
    """Service for managing and enforcing usage quotas."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db

    async def get_global_quota(self) -> Optional[UsageQuota]:
        """Get the global usage quota.

        Returns:
            UsageQuota object or None if not set.
        """
        result = await self.db.execute(
            select(UsageQuota).where(UsageQuota.scope == QuotaScope.GLOBAL)
        )
        return result.scalar_one_or_none()

    async def get_or_create_global_quota(self) -> UsageQuota:
        """Get or create the global usage quota.

        Returns:
            UsageQuota object.
        """
        quota = await self.get_global_quota()
        if not quota:
            quota = UsageQuota(
                scope=QuotaScope.GLOBAL,
                alert_threshold_percent=80,
            )
            self.db.add(quota)
            await self.db.flush()
            await self.db.refresh(quota)
        return quota

    async def update_global_quota(
        self,
        daily_cost_limit_usd: Optional[Decimal] = None,
        monthly_cost_limit_usd: Optional[Decimal] = None,
        daily_token_limit: Optional[int] = None,
        monthly_token_limit: Optional[int] = None,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
        alert_threshold_percent: Optional[int] = None,
    ) -> UsageQuota:
        """Update the global usage quota.

        Args:
            daily_cost_limit_usd: Daily cost limit in USD.
            monthly_cost_limit_usd: Monthly cost limit in USD.
            daily_token_limit: Daily token limit.
            monthly_token_limit: Monthly token limit.
            requests_per_minute: Rate limit per minute.
            requests_per_hour: Rate limit per hour.
            alert_threshold_percent: Alert threshold (0-100).

        Returns:
            Updated UsageQuota object.
        """
        quota = await self.get_or_create_global_quota()

        if daily_cost_limit_usd is not None:
            quota.daily_cost_limit_usd = daily_cost_limit_usd
        if monthly_cost_limit_usd is not None:
            quota.monthly_cost_limit_usd = monthly_cost_limit_usd
        if daily_token_limit is not None:
            quota.daily_token_limit = daily_token_limit
        if monthly_token_limit is not None:
            quota.monthly_token_limit = monthly_token_limit
        if requests_per_minute is not None:
            quota.requests_per_minute = requests_per_minute
        if requests_per_hour is not None:
            quota.requests_per_hour = requests_per_hour
        if alert_threshold_percent is not None:
            quota.alert_threshold_percent = alert_threshold_percent

        await self.db.flush()
        await self.db.refresh(quota)
        return quota

    async def get_user_quota(self, user_id: UUID) -> Optional[UsageQuota]:
        """Get a user's usage quota.

        Args:
            user_id: User's UUID.

        Returns:
            UsageQuota object or None if not set.
        """
        result = await self.db.execute(
            select(UsageQuota)
            .where(UsageQuota.scope == QuotaScope.USER)
            .where(UsageQuota.scope_id == str(user_id))
        )
        return result.scalar_one_or_none()

    async def set_user_quota(
        self,
        user_id: UUID,
        daily_cost_limit_usd: Optional[Decimal] = None,
        monthly_cost_limit_usd: Optional[Decimal] = None,
        daily_token_limit: Optional[int] = None,
        monthly_token_limit: Optional[int] = None,
    ) -> UsageQuota:
        """Set or update a user's usage quota.

        Args:
            user_id: User's UUID.
            daily_cost_limit_usd: Daily cost limit in USD.
            monthly_cost_limit_usd: Monthly cost limit in USD.
            daily_token_limit: Daily token limit.
            monthly_token_limit: Monthly token limit.

        Returns:
            UsageQuota object.
        """
        quota = await self.get_user_quota(user_id)

        if not quota:
            quota = UsageQuota(
                scope=QuotaScope.USER,
                scope_id=str(user_id),
                alert_threshold_percent=80,
            )
            self.db.add(quota)

        if daily_cost_limit_usd is not None:
            quota.daily_cost_limit_usd = daily_cost_limit_usd
        if monthly_cost_limit_usd is not None:
            quota.monthly_cost_limit_usd = monthly_cost_limit_usd
        if daily_token_limit is not None:
            quota.daily_token_limit = daily_token_limit
        if monthly_token_limit is not None:
            quota.monthly_token_limit = monthly_token_limit

        await self.db.flush()
        await self.db.refresh(quota)
        return quota

    async def get_current_usage(
        self,
        user_id: Optional[UUID] = None,
    ) -> dict[str, Any]:
        """Get current usage for today and this month.

        Args:
            user_id: Optional user ID for user-specific usage.

        Returns:
            Dict with daily and monthly usage stats.
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Build base query for daily usage
        daily_query = select(
            func.coalesce(func.sum(UsageLog.total_tokens), 0).label("tokens"),
            func.coalesce(func.sum(UsageLog.cost_usd), Decimal("0")).label("cost"),
        ).where(UsageLog.created_at >= today_start)

        # Build base query for monthly usage
        monthly_query = select(
            func.coalesce(func.sum(UsageLog.total_tokens), 0).label("tokens"),
            func.coalesce(func.sum(UsageLog.cost_usd), Decimal("0")).label("cost"),
        ).where(UsageLog.created_at >= month_start)

        # Note: User-specific usage tracking would require adding user_id to UsageLog
        # For now, we track global usage only

        daily_result = await self.db.execute(daily_query)
        daily_row = daily_result.one()

        monthly_result = await self.db.execute(monthly_query)
        monthly_row = monthly_result.one()

        return {
            "daily_tokens_used": int(daily_row.tokens),
            "daily_cost_used": Decimal(str(daily_row.cost)),
            "monthly_tokens_used": int(monthly_row.tokens),
            "monthly_cost_used": Decimal(str(monthly_row.cost)),
        }

    async def check_quota(self, user_id: Optional[UUID] = None) -> QuotaCheckResult:
        """Check if usage is within quota limits.

        Args:
            user_id: Optional user ID for user-specific quota check.

        Returns:
            QuotaCheckResult with allowed status and current usage.
        """
        # Get current usage
        usage = await self.get_current_usage(user_id)

        # Get applicable quota (user quota if exists, otherwise global)
        quota = None
        if user_id:
            quota = await self.get_user_quota(user_id)
        if not quota:
            quota = await self.get_global_quota()

        result = QuotaCheckResult(
            allowed=True,
            daily_cost_used=usage["daily_cost_used"],
            monthly_cost_used=usage["monthly_cost_used"],
            daily_tokens_used=usage["daily_tokens_used"],
            monthly_tokens_used=usage["monthly_tokens_used"],
        )

        if not quota:
            return result

        # Set limits in result
        result.daily_cost_limit = quota.daily_cost_limit_usd
        result.monthly_cost_limit = quota.monthly_cost_limit_usd
        result.daily_token_limit = quota.daily_token_limit
        result.monthly_token_limit = quota.monthly_token_limit

        # Check daily cost limit
        if quota.daily_cost_limit_usd and usage["daily_cost_used"] >= quota.daily_cost_limit_usd:
            result.allowed = False
            result.reason = "Daily cost limit exceeded"
            return result

        # Check monthly cost limit
        if quota.monthly_cost_limit_usd and usage["monthly_cost_used"] >= quota.monthly_cost_limit_usd:
            result.allowed = False
            result.reason = "Monthly cost limit exceeded"
            return result

        # Check daily token limit
        if quota.daily_token_limit and usage["daily_tokens_used"] >= quota.daily_token_limit:
            result.allowed = False
            result.reason = "Daily token limit exceeded"
            return result

        # Check monthly token limit
        if quota.monthly_token_limit and usage["monthly_tokens_used"] >= quota.monthly_token_limit:
            result.allowed = False
            result.reason = "Monthly token limit exceeded"
            return result

        return result

    async def get_alerts(self, user_id: Optional[UUID] = None) -> list[QuotaAlert]:
        """Get quota alerts for limits that are approaching or exceeded.

        Args:
            user_id: Optional user ID for user-specific alerts.

        Returns:
            List of QuotaAlert objects.
        """
        # Get current usage and quota
        usage = await self.get_current_usage(user_id)

        quota = None
        if user_id:
            quota = await self.get_user_quota(user_id)
        if not quota:
            quota = await self.get_global_quota()

        if not quota:
            return []

        alerts = []
        threshold = quota.alert_threshold_percent

        # Check daily cost
        if quota.daily_cost_limit_usd and quota.daily_cost_limit_usd > 0:
            percent = float(usage["daily_cost_used"] / quota.daily_cost_limit_usd * 100)
            if percent >= threshold:
                alerts.append(QuotaAlert(
                    alert_type="cost",
                    period="daily",
                    current_value=float(usage["daily_cost_used"]),
                    limit_value=float(quota.daily_cost_limit_usd),
                    percent_used=percent,
                    threshold_percent=threshold,
                    is_exceeded=percent >= 100,
                ))

        # Check monthly cost
        if quota.monthly_cost_limit_usd and quota.monthly_cost_limit_usd > 0:
            percent = float(usage["monthly_cost_used"] / quota.monthly_cost_limit_usd * 100)
            if percent >= threshold:
                alerts.append(QuotaAlert(
                    alert_type="cost",
                    period="monthly",
                    current_value=float(usage["monthly_cost_used"]),
                    limit_value=float(quota.monthly_cost_limit_usd),
                    percent_used=percent,
                    threshold_percent=threshold,
                    is_exceeded=percent >= 100,
                ))

        # Check daily tokens
        if quota.daily_token_limit and quota.daily_token_limit > 0:
            percent = usage["daily_tokens_used"] / quota.daily_token_limit * 100
            if percent >= threshold:
                alerts.append(QuotaAlert(
                    alert_type="tokens",
                    period="daily",
                    current_value=usage["daily_tokens_used"],
                    limit_value=quota.daily_token_limit,
                    percent_used=percent,
                    threshold_percent=threshold,
                    is_exceeded=percent >= 100,
                ))

        # Check monthly tokens
        if quota.monthly_token_limit and quota.monthly_token_limit > 0:
            percent = usage["monthly_tokens_used"] / quota.monthly_token_limit * 100
            if percent >= threshold:
                alerts.append(QuotaAlert(
                    alert_type="tokens",
                    period="monthly",
                    current_value=usage["monthly_tokens_used"],
                    limit_value=quota.monthly_token_limit,
                    percent_used=percent,
                    threshold_percent=threshold,
                    is_exceeded=percent >= 100,
                ))

        return alerts

    async def get_usage_status(self, user_id: Optional[UUID] = None) -> dict[str, Any]:
        """Get comprehensive usage status with limits and percentages.

        Args:
            user_id: Optional user ID for user-specific status.

        Returns:
            Dict with current usage, limits, and percentage calculations.
        """
        usage = await self.get_current_usage(user_id)

        quota = None
        if user_id:
            quota = await self.get_user_quota(user_id)
        if not quota:
            quota = await self.get_global_quota()

        result = {
            "daily_cost_used": float(usage["daily_cost_used"]),
            "daily_cost_limit": None,
            "daily_cost_percent": None,
            "monthly_cost_used": float(usage["monthly_cost_used"]),
            "monthly_cost_limit": None,
            "monthly_cost_percent": None,
            "daily_tokens_used": usage["daily_tokens_used"],
            "daily_token_limit": None,
            "daily_token_percent": None,
            "monthly_tokens_used": usage["monthly_tokens_used"],
            "monthly_token_limit": None,
            "monthly_token_percent": None,
        }

        if quota:
            if quota.daily_cost_limit_usd:
                result["daily_cost_limit"] = float(quota.daily_cost_limit_usd)
                result["daily_cost_percent"] = float(usage["daily_cost_used"] / quota.daily_cost_limit_usd * 100)

            if quota.monthly_cost_limit_usd:
                result["monthly_cost_limit"] = float(quota.monthly_cost_limit_usd)
                result["monthly_cost_percent"] = float(usage["monthly_cost_used"] / quota.monthly_cost_limit_usd * 100)

            if quota.daily_token_limit:
                result["daily_token_limit"] = quota.daily_token_limit
                result["daily_token_percent"] = usage["daily_tokens_used"] / quota.daily_token_limit * 100

            if quota.monthly_token_limit:
                result["monthly_token_limit"] = quota.monthly_token_limit
                result["monthly_token_percent"] = usage["monthly_tokens_used"] / quota.monthly_token_limit * 100

        return result


def get_quota_service(db: AsyncSession) -> QuotaService:
    """Factory function to get a QuotaService instance.

    Args:
        db: AsyncSession for database operations.

    Returns:
        QuotaService instance.
    """
    return QuotaService(db)
