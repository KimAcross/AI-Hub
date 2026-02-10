"""API dependencies for dependency injection."""

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import UserRole
from app.services.assistant_service import AssistantService
from app.services.conversation_service import ConversationService


async def get_assistant_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AssistantService:
    """Dependency that provides an AssistantService instance."""
    return AssistantService(db)


async def get_conversation_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ConversationService:
    """Dependency that provides a ConversationService instance."""
    return ConversationService(db)


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request.

    Args:
        request: FastAPI request object.

    Returns:
        Tuple of (client_ip, user_agent).
    """
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip, user_agent


async def verify_admin_token(
    x_admin_token: Annotated[Optional[str], Header()] = None,
) -> dict:
    """Dependency to verify admin JWT authentication.

    Args:
        x_admin_token: Admin JWT token from X-Admin-Token header.

    Returns:
        Token payload dict if valid.

    Raises:
        HTTPException: If token is missing or invalid.
    """
    from app.services.admin_auth_service import get_admin_auth_service

    if not x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin token required",
        )

    auth_service = get_admin_auth_service()
    payload = auth_service.verify_token(x_admin_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin token",
        )

    return payload


async def verify_csrf_token(
    request: Request,
    x_admin_token: Annotated[Optional[str], Header()] = None,
    x_csrf_token: Annotated[Optional[str], Header()] = None,
) -> bool:
    """Dependency to verify CSRF token for state-changing operations.

    Should be used on POST, PATCH, PUT, DELETE endpoints that require admin auth.

    Args:
        request: FastAPI request object.
        x_admin_token: Admin JWT token from X-Admin-Token header.
        x_csrf_token: CSRF token from X-CSRF-Token header.

    Returns:
        True if CSRF token is valid.

    Raises:
        HTTPException: If CSRF token is missing or invalid.
    """
    from app.services.admin_auth_service import get_admin_auth_service

    # Skip CSRF check for safe methods
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return True

    if not x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin token required",
        )

    if not x_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required for this operation",
        )

    auth_service = get_admin_auth_service()
    if not auth_service.verify_csrf(x_admin_token, x_csrf_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )

    return True


async def verify_user_token(
    x_admin_token: Annotated[Optional[str], Header()] = None,
) -> dict:
    """Dependency to verify user JWT authentication.

    Supports both legacy admin tokens (sub="admin") and new user tokens.

    Args:
        x_admin_token: JWT token from X-Admin-Token header.

    Returns:
        Token payload dict if valid.

    Raises:
        HTTPException: If token is missing or invalid.
    """
    from app.services.admin_auth_service import get_admin_auth_service

    if not x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
        )

    auth_service = get_admin_auth_service()
    payload = auth_service.verify_token(x_admin_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # For legacy admin tokens, set role to admin
    if payload.get("sub") == "admin":
        payload["role"] = UserRole.ADMIN.value

    return payload


async def require_role(
    required_roles: list[UserRole],
    x_admin_token: Annotated[Optional[str], Header()] = None,
) -> dict:
    """Dependency factory for role-based access control.

    Args:
        required_roles: List of roles that are allowed.
        x_admin_token: JWT token from header.

    Returns:
        Token payload if role is allowed.

    Raises:
        HTTPException: If role is not allowed.
    """
    payload = await verify_user_token(x_admin_token)

    # Get role from token
    role_value = payload.get("role")

    # Legacy admin tokens always have admin role
    if payload.get("sub") == "admin":
        return payload

    if not role_value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    try:
        user_role = UserRole(role_value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role in token",
        )

    if user_role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this operation",
        )

    return payload


async def require_admin_role(
    x_admin_token: Annotated[Optional[str], Header()] = None,
) -> dict:
    """Dependency that requires admin role.

    Returns:
        Token payload if user is admin.
    """
    return await require_role([UserRole.ADMIN], x_admin_token)


async def require_manager_role(
    x_admin_token: Annotated[Optional[str], Header()] = None,
) -> dict:
    """Dependency that requires manager role or higher.

    Returns:
        Token payload if user is manager or admin.
    """
    return await require_role([UserRole.ADMIN, UserRole.MANAGER], x_admin_token)


async def require_any_role(
    x_admin_token: Annotated[Optional[str], Header()] = None,
) -> dict:
    """Dependency that requires any authenticated role.

    Returns:
        Token payload if user has any role.
    """
    return await require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.USER], x_admin_token)
