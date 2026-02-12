"""User management API endpoints."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_info, get_db, require_admin_role, require_any_role, require_manager_role, verify_csrf_token
from app.core.rate_limit import limiter
from app.models.user import UserRole
from app.schemas.user import (
    UserApiKeyCreate,
    UserApiKeyCreateResponse,
    UserApiKeyResponse,
    UserCreate,
    UserListResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserPasswordChange,
    UserResponse,
    UserUpdate,
)
from app.services.audit_service import AuditService
from app.services.user_auth_service import UserAuthService
from app.services.user_service import UserEmailExistsError, UserNotFoundError, UserService

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_user(
    request: Request,
    data: UserCreate,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user (Admin only).

    Args:
        data: User creation data.

    Returns:
        Created user.
    """
    user_service = UserService(db)
    audit_service = AuditService(db)

    try:
        user = await user_service.create_user(
            email=data.email,
            password=data.password,
            name=data.name,
            role=data.role,
        )

        ip, user_agent = get_client_info(request)
        await audit_service.log_user_action(
            action="created",
            user_id=str(user.id),
            actor=_admin.get("email", "admin"),
            actor_id=_admin.get("sub"),
            ip_address=ip,
            user_agent=user_agent,
            new_values={"email": user.email, "name": user.name, "role": user.role.value},
        )

        await db.commit()
        return UserResponse.model_validate(user)

    except UserEmailExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )


@router.get("", response_model=UserListResponse)
@limiter.limit("30/minute")
async def list_users(
    request: Request,
    _auth: Annotated[dict, Depends(require_manager_role)],
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
) -> UserListResponse:
    """List users with filtering and pagination (Manager+).

    Returns:
        Paginated list of users.
    """
    user_service = UserService(db)
    users, total = await user_service.list_users(
        search=search,
        role=role,
        is_active=is_active,
        page=page,
        size=size,
    )

    pages = (total + size - 1) // size if size > 0 else 0

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit("30/minute")
async def get_user(
    request: Request,
    user_id: UUID,
    _auth: Annotated[dict, Depends(require_manager_role)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get a user by ID (Manager+).

    Returns:
        User details.
    """
    user_service = UserService(db)

    try:
        user = await user_service.get_user(user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.patch("/{user_id}", response_model=UserResponse)
@limiter.limit("10/minute")
async def update_user(
    request: Request,
    user_id: UUID,
    data: UserUpdate,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update a user (Admin only).

    Returns:
        Updated user.
    """
    user_service = UserService(db)
    audit_service = AuditService(db)

    try:
        # Get old values for audit
        old_user = await user_service.get_user(user_id)
        old_values = {
            "email": old_user.email,
            "name": old_user.name,
            "role": old_user.role.value,
        }

        user = await user_service.update_user(
            user_id=user_id,
            email=data.email,
            name=data.name,
            role=data.role,
        )

        new_values = {
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
        }

        ip, user_agent = get_client_info(request)
        await audit_service.log_user_action(
            action="updated",
            user_id=str(user.id),
            actor=_admin.get("email", "admin"),
            actor_id=_admin.get("sub"),
            ip_address=ip,
            user_agent=user_agent,
            old_values=old_values,
            new_values=new_values,
        )

        await db.commit()
        return UserResponse.model_validate(user)

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except UserEmailExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )


@router.post("/{user_id}/disable", response_model=UserResponse)
@limiter.limit("10/minute")
async def disable_user(
    request: Request,
    user_id: UUID,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Disable a user account (Admin only).

    Returns:
        Updated user.
    """
    user_service = UserService(db)
    audit_service = AuditService(db)

    try:
        user = await user_service.disable_user(user_id)

        ip, user_agent = get_client_info(request)
        await audit_service.log_user_action(
            action="disabled",
            user_id=str(user.id),
            actor=_admin.get("email", "admin"),
            actor_id=_admin.get("sub"),
            ip_address=ip,
            user_agent=user_agent,
        )

        await db.commit()
        return UserResponse.model_validate(user)

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.post("/{user_id}/enable", response_model=UserResponse)
@limiter.limit("10/minute")
async def enable_user(
    request: Request,
    user_id: UUID,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Enable a disabled user account (Admin only).

    Returns:
        Updated user.
    """
    user_service = UserService(db)
    audit_service = AuditService(db)

    try:
        user = await user_service.enable_user(user_id)

        ip, user_agent = get_client_info(request)
        await audit_service.log_user_action(
            action="enabled",
            user_id=str(user.id),
            actor=_admin.get("email", "admin"),
            actor_id=_admin.get("sub"),
            ip_address=ip,
            user_agent=user_agent,
        )

        await db.commit()
        return UserResponse.model_validate(user)

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_user(
    request: Request,
    user_id: UUID,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a user (Admin only).

    Hard deletes the user from the database.
    """
    user_service = UserService(db)
    audit_service = AuditService(db)

    try:
        # Get user info before deletion for audit
        user = await user_service.get_user(user_id)
        user_info = {"email": user.email, "name": user.name}

        await user_service.delete_user(user_id)

        ip, user_agent = get_client_info(request)
        await audit_service.log_user_action(
            action="deleted",
            user_id=str(user_id),
            actor=_admin.get("email", "admin"),
            actor_id=_admin.get("sub"),
            ip_address=ip,
            user_agent=user_agent,
            old_values=user_info,
        )

        await db.commit()

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def reset_user_password(
    request: Request,
    user_id: UUID,
    data: UserPasswordChange,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Reset a user's password (Admin only)."""
    user_service = UserService(db)
    audit_service = AuditService(db)

    try:
        await user_service.change_password(user_id, data.new_password)

        ip, user_agent = get_client_info(request)
        await audit_service.log_user_action(
            action="password_reset",
            user_id=str(user_id),
            actor=_admin.get("email", "admin"),
            actor_id=_admin.get("sub"),
            ip_address=ip,
            user_agent=user_agent,
        )

        await db.commit()

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


# Auth endpoints for user login
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login", response_model=UserLoginResponse)
@limiter.limit("5/minute")
async def user_login(
    request: Request,
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> UserLoginResponse:
    """Login with email and password.

    Returns:
        JWT token and user details.
    """
    auth_service = UserAuthService(db)
    audit_service = AuditService(db)

    ip, user_agent = get_client_info(request)

    user = await auth_service.authenticate(data.email, data.password)

    if not user:
        # Log failed attempt
        await audit_service.log_login(
            user_id="unknown",
            email=data.email,
            ip_address=ip,
            user_agent=user_agent,
            success=False,
        )
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token, expires_at, csrf_token = auth_service.generate_token(user)

    # Log successful login
    await audit_service.log_login(
        user_id=str(user.id),
        email=user.email,
        ip_address=ip,
        user_agent=user_agent,
        success=True,
    )
    await db.commit()
    await db.refresh(user)

    return UserLoginResponse(
        token=token,
        expires_at=expires_at,
        csrf_token=csrf_token,
        user=UserResponse.model_validate(user),
    )


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user(
    _auth: Annotated[dict, Depends(require_any_role)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get current authenticated user.

    Returns:
        Current user details.
    """
    user_service = UserService(db)

    try:
        user_id = UUID(_auth["sub"])
        user = await user_service.get_user(user_id)
        return UserResponse.model_validate(user)
    except (KeyError, ValueError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@auth_router.get("/verify")
async def verify_token(
    _auth: Annotated[dict, Depends(require_any_role)],
) -> dict:
    """Verify that the current token is valid.

    Returns:
        Dict with valid=True and user role.
    """
    return {
        "valid": True,
        "role": _auth.get("role"),
        "sub": _auth.get("sub"),
    }


@auth_router.get("/usage")
async def get_user_usage(
    _auth: Annotated[dict, Depends(require_any_role)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get usage statistics for the current user.

    Returns:
        Usage status with limits and percentages.
    """
    from app.services.quota_service import QuotaService

    quota_service = QuotaService(db)

    # Get user_id from token (None for legacy admin tokens)
    user_id = None
    sub = _auth.get("sub")
    if sub and sub != "admin":
        try:
            user_id = UUID(sub)
        except ValueError:
            pass

    usage = await quota_service.get_usage_status(user_id)
    return usage
