"""Usage log service for tracking token usage and costs."""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage_log import UsageLog
from app.services.openrouter_service import OpenRouterService, get_openrouter_service


class UsageLogService:
    """Service for logging and querying token usage and costs."""

    def __init__(
        self,
        db: AsyncSession,
        openrouter_service: Optional[OpenRouterService] = None,
    ):
        """Initialize the service.

        Args:
            db: Database session.
            openrouter_service: OpenRouter service for pricing lookups.
        """
        self.db = db
        self.openrouter = openrouter_service or get_openrouter_service()

    async def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ) -> Decimal:
        """Calculate the cost in USD for token usage.

        Args:
            prompt_tokens: Number of prompt tokens.
            completion_tokens: Number of completion tokens.
            model: Model ID used.

        Returns:
            Cost in USD as Decimal with 6 decimal places.
        """
        try:
            pricing = await self.openrouter.get_model_pricing(model)

            # Pricing is in USD per 1M tokens
            prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
            completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]

            total_cost = prompt_cost + completion_cost

            # Round to 6 decimal places
            return Decimal(str(total_cost)).quantize(Decimal("0.000001"))
        except Exception:
            # Return zero cost if pricing lookup fails
            return Decimal("0")

    async def log_usage(
        self,
        assistant_id: Optional[uuid.UUID],
        conversation_id: Optional[uuid.UUID],
        message_id: Optional[uuid.UUID],
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> UsageLog:
        """Log token usage for a message.

        Args:
            assistant_id: ID of the assistant (optional).
            conversation_id: ID of the conversation (optional).
            message_id: ID of the message (optional).
            model: Model ID used.
            prompt_tokens: Number of prompt tokens.
            completion_tokens: Number of completion tokens.

        Returns:
            Created UsageLog entry.
        """
        total_tokens = prompt_tokens + completion_tokens
        cost_usd = await self.calculate_cost(prompt_tokens, completion_tokens, model)

        usage_log = UsageLog(
            assistant_id=assistant_id,
            conversation_id=conversation_id,
            message_id=message_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
        )

        self.db.add(usage_log)
        await self.db.flush()
        await self.db.refresh(usage_log)

        return usage_log

    async def get_summary(
        self,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """Get usage summary for a time period.

        Args:
            period_start: Start of period (defaults to 30 days ago).
            period_end: End of period (defaults to now).

        Returns:
            Summary with total tokens, cost, and counts.
        """
        now = datetime.now(timezone.utc)
        period_end = period_end or now
        period_start = period_start or (now - timedelta(days=30))

        query = select(
            func.coalesce(func.sum(UsageLog.total_tokens), 0).label("total_tokens"),
            func.coalesce(func.sum(UsageLog.prompt_tokens), 0).label(
                "total_prompt_tokens"
            ),
            func.coalesce(func.sum(UsageLog.completion_tokens), 0).label(
                "total_completion_tokens"
            ),
            func.coalesce(func.sum(UsageLog.cost_usd), Decimal("0")).label(
                "total_cost_usd"
            ),
            func.count(func.distinct(UsageLog.conversation_id)).label(
                "total_conversations"
            ),
            func.count().label("total_messages"),
        ).where(
            UsageLog.created_at >= period_start,
            UsageLog.created_at <= period_end,
        )

        result = await self.db.execute(query)
        row = result.one()

        return {
            "total_tokens": int(row.total_tokens),
            "total_prompt_tokens": int(row.total_prompt_tokens),
            "total_completion_tokens": int(row.total_completion_tokens),
            "total_cost_usd": Decimal(str(row.total_cost_usd)),
            "total_conversations": int(row.total_conversations),
            "total_messages": int(row.total_messages),
            "period_start": period_start,
            "period_end": period_end,
        }

    async def get_breakdown_by_model(self) -> list[dict[str, Any]]:
        """Get usage breakdown by model.

        Returns:
            List of usage stats per model, sorted by cost descending.
        """
        query = (
            select(
                UsageLog.model,
                func.sum(UsageLog.total_tokens).label("total_tokens"),
                func.sum(UsageLog.prompt_tokens).label("prompt_tokens"),
                func.sum(UsageLog.completion_tokens).label("completion_tokens"),
                func.sum(UsageLog.cost_usd).label("cost_usd"),
                func.count().label("message_count"),
            )
            .group_by(UsageLog.model)
            .order_by(func.sum(UsageLog.cost_usd).desc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "model": row.model,
                "total_tokens": int(row.total_tokens or 0),
                "prompt_tokens": int(row.prompt_tokens or 0),
                "completion_tokens": int(row.completion_tokens or 0),
                "cost_usd": Decimal(str(row.cost_usd or 0)),
                "message_count": int(row.message_count or 0),
            }
            for row in rows
        ]

    async def get_breakdown_by_assistant(self) -> list[dict[str, Any]]:
        """Get usage breakdown by assistant.

        Returns:
            List of usage stats per assistant, sorted by cost descending.
        """
        # Import here to avoid circular imports
        from app.models.assistant import Assistant

        query = (
            select(
                UsageLog.assistant_id,
                Assistant.name.label("assistant_name"),
                func.sum(UsageLog.total_tokens).label("total_tokens"),
                func.sum(UsageLog.prompt_tokens).label("prompt_tokens"),
                func.sum(UsageLog.completion_tokens).label("completion_tokens"),
                func.sum(UsageLog.cost_usd).label("cost_usd"),
                func.count().label("message_count"),
            )
            .outerjoin(Assistant, UsageLog.assistant_id == Assistant.id)
            .group_by(UsageLog.assistant_id, Assistant.name)
            .order_by(func.sum(UsageLog.cost_usd).desc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "assistant_id": str(row.assistant_id) if row.assistant_id else None,
                "assistant_name": row.assistant_name or "Unknown",
                "total_tokens": int(row.total_tokens or 0),
                "prompt_tokens": int(row.prompt_tokens or 0),
                "completion_tokens": int(row.completion_tokens or 0),
                "cost_usd": Decimal(str(row.cost_usd or 0)),
                "message_count": int(row.message_count or 0),
            }
            for row in rows
        ]

    async def get_daily_usage(self, days: int = 30) -> list[dict[str, Any]]:
        """Get daily usage for the last N days.

        Args:
            days: Number of days to retrieve (default 30).

        Returns:
            List of daily usage stats, sorted by date ascending.
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        query = (
            select(
                func.date(UsageLog.created_at).label("date"),
                func.sum(UsageLog.total_tokens).label("total_tokens"),
                func.sum(UsageLog.prompt_tokens).label("prompt_tokens"),
                func.sum(UsageLog.completion_tokens).label("completion_tokens"),
                func.sum(UsageLog.cost_usd).label("cost_usd"),
                func.count().label("message_count"),
            )
            .where(UsageLog.created_at >= start_date)
            .group_by(func.date(UsageLog.created_at))
            .order_by(func.date(UsageLog.created_at).asc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "date": str(row.date),
                "total_tokens": int(row.total_tokens or 0),
                "prompt_tokens": int(row.prompt_tokens or 0),
                "completion_tokens": int(row.completion_tokens or 0),
                "cost_usd": Decimal(str(row.cost_usd or 0)),
                "message_count": int(row.message_count or 0),
            }
            for row in rows
        ]


def get_usage_log_service(
    db: AsyncSession,
    openrouter_service: Optional[OpenRouterService] = None,
) -> UsageLogService:
    """Get a UsageLogService instance.

    Args:
        db: Database session.
        openrouter_service: Optional OpenRouter service.

    Returns:
        UsageLogService instance.
    """
    return UsageLogService(db=db, openrouter_service=openrouter_service)
