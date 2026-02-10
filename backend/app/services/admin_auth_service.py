"""Admin authentication service using JWT and bcrypt."""

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.security import generate_csrf_token, verify_password


class AdminAuthService:
    """Service for admin authentication using JWT tokens."""

    ALGORITHM = "HS256"

    def __init__(self) -> None:
        """Initialize the admin auth service."""
        settings = get_settings()
        self.admin_password = settings.admin_password
        self.secret_key = settings.secret_key
        self.token_expire_hours = settings.access_token_expire_hours

    def verify_admin_password(self, password: str) -> bool:
        """Verify the admin password.

        Supports both bcrypt-hashed passwords (production) and
        plaintext passwords (development only).

        Args:
            password: Password to verify.

        Returns:
            True if password matches, False otherwise.
        """
        if not self.admin_password:
            return False
        return verify_password(password, self.admin_password)

    def generate_token(self) -> tuple[str, datetime, str]:
        """Generate a JWT admin session token with CSRF token.

        Returns:
            Tuple of (JWT token, expiry datetime, CSRF token).
        """
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(hours=self.token_expire_hours)
        csrf_token = generate_csrf_token()

        payload = {
            "sub": "admin",
            "exp": expiry,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "csrf": csrf_token,
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
        return token, expiry, csrf_token

    def verify_token(self, token: str) -> dict | None:
        """Verify a JWT admin session token.

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
            # Verify it's an admin token
            if payload.get("sub") != "admin":
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
        return payload.get("csrf") == csrf_token


def get_admin_auth_service() -> AdminAuthService:
    """Get an instance of AdminAuthService.

    Returns:
        AdminAuthService instance.
    """
    return AdminAuthService()
