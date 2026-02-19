"""Settings API endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin_role, require_any_role
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.schemas.settings import SettingsResponse, SettingsUpdate
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SettingsResponse)
async def get_application_settings(
    db: AsyncSession = Depends(get_db),
    _auth: dict = Depends(require_any_role),
) -> SettingsResponse:
    """Get current application settings."""
    config = get_settings()
    service = SettingsService(db)

    # Check if API key is set (either in env or database)
    db_api_key = await service.get_openrouter_api_key()
    api_key_set = bool(config.openrouter_api_key or db_api_key)

    # Get all settings from database
    default_model = await service.get_default_model()
    language = await service.get_language()
    streaming_enabled = await service.get_streaming_enabled()
    auto_save_interval = await service.get_auto_save_interval()

    return SettingsResponse(
        openrouter_api_key_set=api_key_set,
        default_model=default_model,
        embedding_model=config.embedding_model,
        max_file_size_mb=config.max_file_size_mb,
        language=language,
        streaming_enabled=streaming_enabled,
        auto_save_interval=auto_save_interval,
    )


@router.patch("", response_model=SettingsResponse)
@limiter.limit("10/minute")
async def update_application_settings(
    request: Request,
    settings: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _auth: dict = Depends(require_admin_role),
) -> SettingsResponse:
    """Update application settings."""
    config = get_settings()
    service = SettingsService(db)

    if settings.openrouter_api_key is not None:
        await service.set_openrouter_api_key(
            settings.openrouter_api_key if settings.openrouter_api_key else None
        )

    if settings.default_model is not None:
        await service.set_default_model(settings.default_model)

    if settings.language is not None:
        await service.set_language(settings.language)

    if settings.streaming_enabled is not None:
        await service.set_streaming_enabled(settings.streaming_enabled)

    if settings.auto_save_interval is not None:
        await service.set_auto_save_interval(settings.auto_save_interval)

    # Return updated settings
    db_api_key = await service.get_openrouter_api_key()
    api_key_set = bool(config.openrouter_api_key or db_api_key)
    default_model = await service.get_default_model()
    language = await service.get_language()
    streaming_enabled = await service.get_streaming_enabled()
    auto_save_interval = await service.get_auto_save_interval()

    return SettingsResponse(
        openrouter_api_key_set=api_key_set,
        default_model=default_model,
        embedding_model=config.embedding_model,
        max_file_size_mb=config.max_file_size_mb,
        language=language,
        streaming_enabled=streaming_enabled,
        auto_save_interval=auto_save_interval,
    )


@router.post("/test-api-key")
@limiter.limit("10/minute")
async def test_openrouter_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _auth: dict = Depends(require_admin_role),
) -> dict:
    """Test if the configured OpenRouter API key is valid."""
    import httpx

    config = get_settings()
    service = SettingsService(db)

    # Get API key from database or environment
    api_key = await service.get_openrouter_api_key() or config.openrouter_api_key

    if not api_key:
        return {"valid": False, "error": "No API key configured"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.openrouter_base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )

            if response.status_code == 200:
                return {"valid": True}
            elif response.status_code == 401:
                return {"valid": False, "error": "Invalid API key"}
            else:
                return {
                    "valid": False,
                    "error": f"API returned status {response.status_code}",
                }
    except httpx.TimeoutException:
        return {"valid": False, "error": "Connection timed out"}
    except Exception as e:
        return {"valid": False, "error": str(e)}
