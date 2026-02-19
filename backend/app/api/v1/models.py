"""Models API endpoints for listing available LLM models."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_any_role
from app.api.deps import get_db

from app.core.cache import get_cache
from app.core.config import get_settings
from app.core.exceptions import OpenRouterError
from app.schemas.conversation import ModelInfo, ModelsListResponse
from app.services.openrouter_service import get_openrouter_service
from app.services.settings_service import SettingsService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/models", tags=["models"])
logger = logging.getLogger(__name__)

# Cache TTL for models list (5 minutes)
MODELS_CACHE_TTL = 300
MODELS_CACHE_KEY = "openrouter:models"


@router.get(
    "",
    response_model=ModelsListResponse,
    summary="List available models",
)
async def list_models(
    _auth: dict = Depends(require_any_role),
    db: AsyncSession = Depends(get_db),
) -> ModelsListResponse:
    """Get a list of all available LLM models from OpenRouter.

    Models are sorted with featured models (Claude, GPT-4, Gemini, etc.) first,
    followed by other models alphabetically.

    Results are cached for 5 minutes to reduce API calls.
    """
    cache = await get_cache()

    # Check cache first
    cached_models = await cache.get(MODELS_CACHE_KEY)
    if cached_models is not None:
        return ModelsListResponse(models=cached_models)

    config = get_settings()
    settings_service = SettingsService(db)
    api_key = (
        await settings_service.get_openrouter_api_key() or config.openrouter_api_key
    )
    service = get_openrouter_service(api_key=api_key)

    try:
        models_data = await service.list_models()
        models = [
            ModelInfo(
                id=m["id"],
                name=m["name"],
                description=m.get("description"),
                context_length=m["context_length"],
                pricing=m.get("pricing"),
            )
            for m in models_data
        ]

        # Cache the result
        await cache.set(MODELS_CACHE_KEY, models, MODELS_CACHE_TTL)

        return ModelsListResponse(models=models)
    except OpenRouterError as e:
        logger.warning("OpenRouter unavailable while fetching models: %s", e)
        return ModelsListResponse(models=[])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models: {str(e)}",
        )
