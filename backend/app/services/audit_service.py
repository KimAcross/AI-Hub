"""Audit service for logging and querying administrative actions."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditService:
    """Service for logging and querying audit events."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        actor: str = "system",
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
    ) -> AuditLog:
        """Log an audit event.

        Args:
            action: Action performed (e.g., "user.created", "api_key.rotated").
            resource_type: Type of resource (e.g., "user", "api_key", "settings").
            resource_id: ID of the affected resource.
            actor: Actor identifier (email or "system").
            actor_id: Actor's user ID if applicable.
            ip_address: Request IP address.
            user_agent: Request user agent.
            details: Additional context about the action.
            old_values: Previous values before change.
            new_values: New values after change.

        Returns:
            Created AuditLog entry.
        """
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor=actor,
            actor_id=actor_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            old_values=old_values,
            new_values=new_values,
        )

        self.db.add(audit_log)
        await self.db.flush()
        await self.db.refresh(audit_log)
        return audit_log

    async def log_user_action(
        self,
        action: str,
        user_id: str,
        actor: str,
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
    ) -> AuditLog:
        """Log a user-related action.

        Args:
            action: Action (e.g., "created", "updated", "disabled").
            user_id: Affected user's ID.
            actor: Actor identifier.
            actor_id: Actor's user ID.
            ip_address: Request IP address.
            user_agent: Request user agent.
            old_values: Previous user values.
            new_values: New user values.

        Returns:
            Created AuditLog entry.
        """
        return await self.log(
            action=f"user.{action}",
            resource_type="user",
            resource_id=user_id,
            actor=actor,
            actor_id=actor_id,
            ip_address=ip_address,
            user_agent=user_agent,
            old_values=old_values,
            new_values=new_values,
        )

    async def log_api_key_action(
        self,
        action: str,
        key_id: str,
        actor: str,
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> AuditLog:
        """Log an API key-related action.

        Args:
            action: Action (e.g., "created", "rotated", "deleted", "tested").
            key_id: API key's ID.
            actor: Actor identifier.
            actor_id: Actor's user ID.
            ip_address: Request IP address.
            user_agent: Request user agent.
            details: Additional details (e.g., provider, name).

        Returns:
            Created AuditLog entry.
        """
        return await self.log(
            action=f"api_key.{action}",
            resource_type="api_key",
            resource_id=key_id,
            actor=actor,
            actor_id=actor_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )

    async def log_quota_action(
        self,
        action: str,
        quota_id: str,
        actor: str,
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
    ) -> AuditLog:
        """Log a quota-related action.

        Args:
            action: Action (e.g., "updated").
            quota_id: Quota's ID.
            actor: Actor identifier.
            actor_id: Actor's user ID.
            ip_address: Request IP address.
            user_agent: Request user agent.
            old_values: Previous quota values.
            new_values: New quota values.

        Returns:
            Created AuditLog entry.
        """
        return await self.log(
            action=f"quota.{action}",
            resource_type="quota",
            resource_id=quota_id,
            actor=actor,
            actor_id=actor_id,
            ip_address=ip_address,
            user_agent=user_agent,
            old_values=old_values,
            new_values=new_values,
        )

    async def log_settings_action(
        self,
        action: str,
        actor: str,
        actor_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
    ) -> AuditLog:
        """Log a settings-related action.

        Args:
            action: Action (e.g., "updated").
            actor: Actor identifier.
            actor_id: Actor's user ID.
            ip_address: Request IP address.
            user_agent: Request user agent.
            old_values: Previous settings.
            new_values: New settings.

        Returns:
            Created AuditLog entry.
        """
        return await self.log(
            action=f"settings.{action}",
            resource_type="settings",
            resource_id=None,
            actor=actor,
            actor_id=actor_id,
            ip_address=ip_address,
            user_agent=user_agent,
            old_values=old_values,
            new_values=new_values,
        )

    async def log_login(
        self,
        user_id: str,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
    ) -> AuditLog:
        """Log a login attempt.

        Args:
            user_id: User's ID.
            email: User's email.
            ip_address: Request IP address.
            user_agent: Request user agent.
            success: Whether login was successful.

        Returns:
            Created AuditLog entry.
        """
        action = "login.success" if success else "login.failed"
        return await self.log(
            action=action,
            resource_type="auth",
            resource_id=user_id,
            actor=email,
            actor_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"success": success},
        )

    async def query(
        self,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        actor: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[AuditLog], int]:
        """Query audit logs with filters.

        Args:
            action: Filter by action (supports prefix matching, e.g., "user").
            resource_type: Filter by resource type.
            resource_id: Filter by resource ID.
            actor: Filter by actor.
            start_date: Filter by start date.
            end_date: Filter by end date.
            limit: Maximum results to return.
            offset: Offset for pagination.

        Returns:
            Tuple of (audit logs list, total count).
        """
        # Build base query
        query = select(AuditLog)

        # Apply filters
        if action:
            if "." in action:
                query = query.where(AuditLog.action == action)
            else:
                query = query.where(AuditLog.action.like(f"{action}.%"))

        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)

        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)

        if actor:
            query = query.where(AuditLog.actor == actor)

        if start_date:
            query = query.where(AuditLog.created_at >= start_date)

        if end_date:
            query = query.where(AuditLog.created_at <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def get_recent(self, limit: int = 50) -> list[AuditLog]:
        """Get recent audit logs.

        Args:
            limit: Maximum results to return.

        Returns:
            List of recent AuditLog entries.
        """
        result = await self.db.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_activity(
        self,
        user_id: str,
        days: int = 30,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get activity for a specific user.

        Args:
            user_id: User's ID.
            days: Number of days to look back.
            limit: Maximum results to return.

        Returns:
            List of AuditLog entries for the user.
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.actor_id == user_id)
            .where(AuditLog.created_at >= start_date)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Get history for a specific resource.

        Args:
            resource_type: Type of resource.
            resource_id: Resource's ID.
            limit: Maximum results to return.

        Returns:
            List of AuditLog entries for the resource.
        """
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.resource_type == resource_type)
            .where(AuditLog.resource_id == resource_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_action_summary(
        self,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """Get summary of actions by type.

        Args:
            days: Number of days to look back.

        Returns:
            List of action summaries with counts.
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(
                AuditLog.action,
                func.count().label("count"),
            )
            .where(AuditLog.created_at >= start_date)
            .group_by(AuditLog.action)
            .order_by(func.count().desc())
        )
        rows = result.all()

        return [
            {"action": row.action, "count": row.count}
            for row in rows
        ]
