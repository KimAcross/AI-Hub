"""API key management endpoints for AI provider keys."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_info, get_db, require_admin_role, verify_csrf_token
from app.core.encryption import decrypt_value
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.models.api_key import APIKeyProvider
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyListResponse,
    APIKeyResponse,
    APIKeyRotate,
    APIKeyTestResponse,
    APIKeyUpdate,
)
from app.services.api_key_service import APIKeyService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin/api-keys", tags=["Admin - API Keys"])


def _key_to_response(key, secret_key: str) -> APIKeyResponse:
    """Convert APIKey model to response with masked key."""
    decrypted = decrypt_value(key.encrypted_key, secret_key)
    masked = (
        f"{decrypted[:4]}...{decrypted[-4:]}"
        if len(decrypted) > 8
        else "*" * len(decrypted)
    )

    return APIKeyResponse(
        id=key.id,
        provider=key.provider,
        name=key.name,
        key_masked=masked,
        is_active=key.is_active,
        is_default=key.is_default,
        last_used_at=key.last_used_at,
        last_tested_at=key.last_tested_at,
        test_status=key.test_status,
        test_error=key.test_error,
        created_at=key.created_at,
        updated_at=key.updated_at,
    )


@router.get("", response_model=APIKeyListResponse)
@limiter.limit("30/minute")
async def list_api_keys(
    request: Request,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
    provider: Optional[APIKeyProvider] = Query(None, description="Filter by provider"),
) -> APIKeyListResponse:
    """List all API keys.

    Returns:
        List of API keys with masked values.
    """
    settings = get_settings()
    key_service = APIKeyService(db)

    keys = await key_service.list_keys(provider)

    return APIKeyListResponse(
        keys=[_key_to_response(k, settings.secret_key) for k in keys],
        total=len(keys),
    )


@router.post("", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_api_key(
    request: Request,
    data: APIKeyCreate,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """Create a new API key.

    Returns:
        Created API key (masked).
    """
    settings = get_settings()
    key_service = APIKeyService(db)
    audit_service = AuditService(db)

    key = await key_service.create_key(
        provider=data.provider,
        name=data.name,
        api_key=data.api_key,
        is_default=data.is_default,
    )

    ip, user_agent = get_client_info(request)
    await audit_service.log_api_key_action(
        action="created",
        key_id=str(key.id),
        actor=_admin.get("email", "admin"),
        actor_id=_admin.get("sub"),
        ip_address=ip,
        user_agent=user_agent,
        details={"provider": key.provider.value, "name": key.name},
    )

    await db.commit()
    return _key_to_response(key, settings.secret_key)


@router.get("/{key_id}", response_model=APIKeyResponse)
@limiter.limit("30/minute")
async def get_api_key(
    request: Request,
    key_id: UUID,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """Get an API key by ID.

    Returns:
        API key details (masked).
    """
    settings = get_settings()
    key_service = APIKeyService(db)

    key = await key_service.get_key(key_id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return _key_to_response(key, settings.secret_key)


@router.patch("/{key_id}", response_model=APIKeyResponse)
@limiter.limit("10/minute")
async def update_api_key(
    request: Request,
    key_id: UUID,
    data: APIKeyUpdate,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """Update an API key.

    Returns:
        Updated API key (masked).
    """
    settings = get_settings()
    key_service = APIKeyService(db)
    audit_service = AuditService(db)

    key = await key_service.update_key(
        key_id=key_id,
        name=data.name,
        is_active=data.is_active,
    )

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    ip, user_agent = get_client_info(request)
    await audit_service.log_api_key_action(
        action="updated",
        key_id=str(key.id),
        actor=_admin.get("email", "admin"),
        actor_id=_admin.get("sub"),
        ip_address=ip,
        user_agent=user_agent,
        details={"name": data.name, "is_active": data.is_active},
    )

    await db.commit()
    return _key_to_response(key, settings.secret_key)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_api_key(
    request: Request,
    key_id: UUID,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an API key."""
    key_service = APIKeyService(db)
    audit_service = AuditService(db)

    # Get key info before deletion
    key = await key_service.get_key(key_id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    deleted = await key_service.delete_key(key_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    ip, user_agent = get_client_info(request)
    await audit_service.log_api_key_action(
        action="deleted",
        key_id=str(key_id),
        actor=_admin.get("email", "admin"),
        actor_id=_admin.get("sub"),
        ip_address=ip,
        user_agent=user_agent,
        details={"provider": key.provider.value, "name": key.name},
    )

    await db.commit()


@router.post("/{key_id}/test", response_model=APIKeyTestResponse)
@limiter.limit("10/minute")
async def test_api_key(
    request: Request,
    key_id: UUID,
    _admin: Annotated[dict, Depends(require_admin_role)],
    db: AsyncSession = Depends(get_db),
) -> APIKeyTestResponse:
    """Test an API key's connectivity.

    Returns:
        Test result with validity and latency.
    """
    key_service = APIKeyService(db)
    audit_service = AuditService(db)

    result = await key_service.test_key(key_id)

    ip, user_agent = get_client_info(request)
    await audit_service.log_api_key_action(
        action="tested",
        key_id=str(key_id),
        actor=_admin.get("email", "admin"),
        actor_id=_admin.get("sub"),
        ip_address=ip,
        user_agent=user_agent,
        details={"valid": result["valid"], "error": result["error"]},
    )

    await db.commit()

    return APIKeyTestResponse(
        valid=result["valid"],
        error=result["error"],
        latency_ms=result["latency_ms"],
    )


@router.post("/{key_id}/rotate", response_model=APIKeyResponse)
@limiter.limit("10/minute")
async def rotate_api_key(
    request: Request,
    key_id: UUID,
    data: APIKeyRotate,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """Rotate an API key with a new value.

    Creates a new key and deactivates the old one.

    Returns:
        New API key (masked).
    """
    settings = get_settings()
    key_service = APIKeyService(db)
    audit_service = AuditService(db)

    new_key = await key_service.rotate_key(key_id, data.new_api_key)

    if not new_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    ip, user_agent = get_client_info(request)
    await audit_service.log_api_key_action(
        action="rotated",
        key_id=str(new_key.id),
        actor=_admin.get("email", "admin"),
        actor_id=_admin.get("sub"),
        ip_address=ip,
        user_agent=user_agent,
        details={"old_key_id": str(key_id), "provider": new_key.provider.value},
    )

    await db.commit()
    return _key_to_response(new_key, settings.secret_key)


@router.post("/{key_id}/set-default", response_model=APIKeyResponse)
@limiter.limit("10/minute")
async def set_default_api_key(
    request: Request,
    key_id: UUID,
    _admin: Annotated[dict, Depends(require_admin_role)],
    _csrf: Annotated[bool, Depends(verify_csrf_token)],
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    """Set an API key as the default for its provider.

    Returns:
        Updated API key (masked).
    """
    settings = get_settings()
    key_service = APIKeyService(db)
    audit_service = AuditService(db)

    key = await key_service.set_default(key_id)

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    ip, user_agent = get_client_info(request)
    await audit_service.log_api_key_action(
        action="set_default",
        key_id=str(key.id),
        actor=_admin.get("email", "admin"),
        actor_id=_admin.get("sub"),
        ip_address=ip,
        user_agent=user_agent,
        details={"provider": key.provider.value},
    )

    await db.commit()
    return _key_to_response(key, settings.secret_key)
