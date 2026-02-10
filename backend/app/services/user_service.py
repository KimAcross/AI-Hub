"""User service for CRUD operations."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import hash_password
from app.models.user import User, UserRole


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found."""

    def __init__(self, user_id: str):
        super().__init__(f"User not found: {user_id}")


class UserEmailExistsError(ValidationError):
    """Raised when a user email already exists."""

    def __init__(self, email: str):
        super().__init__(f"User with email already exists: {email}")


class UserService:
    """Service class for user CRUD operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db

    async def create_user(
        self,
        email: str,
        password: str,
        name: str,
        role: UserRole = UserRole.USER,
        is_verified: bool = False,
    ) -> User:
        """Create a new user.

        Args:
            email: User's email address.
            password: Plain text password (will be hashed).
            name: User's display name.
            role: User's role (default: USER).
            is_verified: Whether the user is verified (default: False).

        Returns:
            Created User object.

        Raises:
            UserEmailExistsError: If email already exists.
        """
        # Check if email exists
        existing = await self.get_user_by_email(email)
        if existing:
            raise UserEmailExistsError(email)

        user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            name=name.strip(),
            role=role,
            is_verified=is_verified,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_user(self, user_id: UUID) -> User:
        """Get a user by ID.

        Args:
            user_id: User's UUID.

        Returns:
            User object.

        Raises:
            UserNotFoundError: If user not found.
        """
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.api_keys))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(str(user_id))
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address.

        Args:
            email: User's email address.

        Returns:
            User object or None if not found.
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[User], int]:
        """List users with filtering and pagination.

        Args:
            search: Optional search term for name or email.
            role: Optional role filter.
            is_active: Optional active status filter.
            page: Page number (1-indexed).
            size: Page size.

        Returns:
            Tuple of (users list, total count).
        """
        # Build base query
        query = select(User)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    User.email.ilike(search_term),
                    User.name.ilike(search_term),
                )
            )

        if role is not None:
            query = query.where(User.role == role)

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        offset = (page - 1) * size
        query = query.order_by(User.created_at.desc()).offset(offset).limit(size)

        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def update_user(
        self,
        user_id: UUID,
        email: Optional[str] = None,
        name: Optional[str] = None,
        role: Optional[UserRole] = None,
    ) -> User:
        """Update a user's details.

        Args:
            user_id: User's UUID.
            email: New email address (optional).
            name: New name (optional).
            role: New role (optional).

        Returns:
            Updated User object.

        Raises:
            UserNotFoundError: If user not found.
            UserEmailExistsError: If new email already exists.
        """
        user = await self.get_user(user_id)

        if email is not None:
            email = email.lower().strip()
            if email != user.email:
                existing = await self.get_user_by_email(email)
                if existing:
                    raise UserEmailExistsError(email)
                user.email = email

        if name is not None:
            user.name = name.strip()

        if role is not None:
            user.role = role

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def change_password(self, user_id: UUID, new_password: str) -> None:
        """Change a user's password.

        Args:
            user_id: User's UUID.
            new_password: New plain text password.

        Raises:
            UserNotFoundError: If user not found.
        """
        user = await self.get_user(user_id)
        user.password_hash = hash_password(new_password)
        await self.db.flush()

    async def disable_user(self, user_id: UUID) -> User:
        """Disable a user account.

        Args:
            user_id: User's UUID.

        Returns:
            Updated User object.

        Raises:
            UserNotFoundError: If user not found.
        """
        user = await self.get_user(user_id)
        user.is_active = False
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def enable_user(self, user_id: UUID) -> User:
        """Enable a disabled user account.

        Args:
            user_id: User's UUID.

        Returns:
            Updated User object.

        Raises:
            UserNotFoundError: If user not found.
        """
        user = await self.get_user(user_id)
        user.is_active = True
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> None:
        """Delete a user (hard delete).

        Args:
            user_id: User's UUID.

        Raises:
            UserNotFoundError: If user not found.
        """
        user = await self.get_user(user_id)
        await self.db.delete(user)
        await self.db.flush()

    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp.

        Args:
            user_id: User's UUID.
        """
        user = await self.get_user(user_id)
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def verify_user(self, user_id: UUID) -> User:
        """Mark a user as verified.

        Args:
            user_id: User's UUID.

        Returns:
            Updated User object.
        """
        user = await self.get_user(user_id)
        user.is_verified = True
        await self.db.flush()
        await self.db.refresh(user)
        return user
