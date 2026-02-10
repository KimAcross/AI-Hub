"""Security utilities for authentication."""

import secrets

import bcrypt


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: The plaintext password

    Returns:
        The bcrypt hash as a string
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify a password against a stored hash or plaintext.

    Supports both bcrypt-hashed passwords (prefix $2a$, $2b$, $2y$)
    and legacy plaintext passwords for development.

    Args:
        plain_password: The password to verify
        stored_password: The stored hash or plaintext password

    Returns:
        True if the password matches, False otherwise
    """
    if stored_password.startswith("$2"):
        # bcrypt hash - verify with bcrypt
        try:
            return bcrypt.checkpw(plain_password.encode(), stored_password.encode())
        except (ValueError, TypeError):
            return False
    else:
        # Legacy plaintext password - use constant-time comparison
        return secrets.compare_digest(plain_password, stored_password)


def is_password_hashed(password: str) -> bool:
    """Check if a password is bcrypt hashed."""
    return password.startswith("$2")


def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    return secrets.token_urlsafe(32)
