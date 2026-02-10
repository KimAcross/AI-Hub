"""Models API endpoints for listing available LLM models."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_any_role

from app.core.cache import get_cache
from app.core.exceptions import OpenRouterError
from app.schemas.conversation import ModelInfo, ModelsListResponse
from app.services.openrouter_service import get_openrouter_service

router = APIRouter(prefix="/models", tags=["models"])

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

    service = get_openrouter_service()

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
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models: {str(e)}",
        )
