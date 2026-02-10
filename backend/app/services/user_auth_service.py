"""User authentication service using JWT and bcrypt."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import generate_csrf_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.models.user_api_key import UserApiKey
from app.services.user_service import UserService


class UserAuthService:
    """Service for user authentication using JWT tokens."""

    ALGORITHM = "HS256"

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the user auth service."""
        settings = get_settings()
        self.secret_key = settings.secret_key
        self.token_expire_hours = settings.access_token_expire_hours
        self.db = db
        self.user_service = UserService(db)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password.

        Args:
            email: User's email address.
            password: Plain text password.

        Returns:
            User object if authentication succeeds, None otherwise.
        """
        user = await self.user_service.get_user_by_email(email)
        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        # Update last login
        await self.user_service.update_last_login(user.id)

        return user

    def generate_token(self, user: User) -> tuple[str, datetime, str]:
        """Generate a JWT session token for a user.

        Args:
            user: User object to generate token for.

        Returns:
            Tuple of (JWT token, expiry datetime, CSRF token).
        """
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(hours=self.token_expire_hours)
        csrf_token = generate_csrf_token()

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "exp": expiry,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "csrf": csrf_token,
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
        return token, expiry, csrf_token

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify a JWT session token.

        Args:
            token: JWT token to verify.

        Returns:
            Token payload dict if valid, None otherwise.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.ALGORITHM],
            )
            # Ensure required fields exist
            if not payload.get("sub") or not payload.get("email"):
                return None
            return payload
        except JWTError:
            return None

    def verify_csrf(self, token: str, csrf_token: str) -> bool:
        """Verify CSRF token matches the one in JWT.

        Args:
            token: JWT token containing expected CSRF.
            csrf_token: CSRF token from request header.

        Returns:
            True if CSRF tokens match, False otherwise.
        """
        payload = self.verify_token(token)
        if not payload:
            return False
        return secrets.compare_digest(payload.get("csrf", ""), csrf_token)

    async def get_user_from_token(self, token: str) -> Optional[User]:
        """Get the user associated with a token.

        Args:
            token: JWT token.

        Returns:
            User object if token is valid, None otherwise.
        """
        payload = self.verify_token(token)
        if not payload:
            return None

        try:
            user_id = uuid.UUID(payload["sub"])
            user = await self.user_service.get_user(user_id)
            if not user.is_active:
                return None
            return user
        except (ValueError, KeyError):
            return None

    def get_role_from_token(self, token: str) -> Optional[UserRole]:
        """Get the user role from a token.

        Args:
            token: JWT token.

        Returns:
            UserRole if token is valid, None otherwise.
        """
        payload = self.verify_token(token)
        if not payload:
            return None

        role_value = payload.get("role")
        if not role_value:
            return None

        try:
            return UserRole(role_value)
        except ValueError:
            return None

    async def verify_api_key(self, api_key: str) -> Optional[User]:
        """Verify a user API key and return the associated user.

        Args:
            api_key: API key string.

        Returns:
            User object if API key is valid, None otherwise.
        """
        if not api_key or len(api_key) < 8:
            return None

        # Get prefix for lookup
        key_prefix = api_key[:8]

        # Find keys with matching prefix
        from sqlalchemy import select

        result = await self.db.execute(
            select(UserApiKey)
            .where(UserApiKey.key_prefix == key_prefix)
            .where(UserApiKey.is_active == True)  # noqa: E712
        )
        keys = result.scalars().all()

        # Check each key (there should typically be only one)
        for user_key in keys:
            # Check expiration
            if user_key.expires_at and user_key.expires_at < datetime.now(timezone.utc):
                continue

            # Verify the full key hash
            if verify_password(api_key, user_key.key_hash):
                # Update last used
                user_key.last_used_at = datetime.now(timezone.utc)
                await self.db.flush()

                # Get the user
                user = await self.user_service.get_user(user_key.user_id)
                if user and user.is_active:
                    return user

        return None

    async def create_api_key(
        self,
        user_id: uuid.UUID,
        name: str,
        expires_in_days: Optional[int] = None,
    ) -> tuple[UserApiKey, str]:
        """Create a new API key for a user.

        Args:
            user_id: User's UUID.
            name: Name/description for the key.
            expires_in_days: Optional expiration in days.

        Returns:
            Tuple of (UserApiKey object, unhashed key string).
            The unhashed key is only returned once at creation.
        """
        # Generate a secure random key
        raw_key = secrets.token_urlsafe(32)
        key_prefix = raw_key[:8]
        key_hash = hash_password(raw_key)

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        api_key = UserApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            expires_at=expires_at,
            is_active=True,
        )

        self.db.add(api_key)
        await self.db.flush()
        await self.db.refresh(api_key)

        return api_key, raw_key

    async def revoke_api_key(self, key_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Revoke a user's API key.

        Args:
            key_id: API key UUID.
            user_id: User's UUID (for ownership verification).

        Returns:
            True if key was revoked, False if not found or not owned.
        """
        from sqlalchemy import select

        result = await self.db.execute(
            select(UserApiKey)
            .where(UserApiKey.id == key_id)
            .where(UserApiKey.user_id == user_id)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return False

        api_key.is_active = False
        await self.db.flush()
        return True

    async def list_user_api_keys(self, user_id: uuid.UUID) -> list[UserApiKey]:
        """List all API keys for a user.

        Args:
            user_id: User's UUID.

        Returns:
            List of UserApiKey objects.
        """
        from sqlalchemy import select

        result = await self.db.execute(
            select(UserApiKey)
            .where(UserApiKey.user_id == user_id)
            .order_by(UserApiKey.created_at.desc())
        )
        return list(result.scalars().all())
