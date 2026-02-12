"""OpenRouter service for chat completions and model listing."""

import json
import time
from typing import Any, AsyncIterator, Optional

import httpx

from app.core.config import get_settings
from app.core.exceptions import OpenRouterError
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Module-level pricing cache
_pricing_cache: dict[str, dict[str, float]] = {}
_pricing_cache_time: float = 0
_PRICING_CACHE_TTL: int = 86400  # 24 hours in seconds


class OpenRouterService:
    """Service for interacting with OpenRouter API."""

    # Popular models to highlight in the model list
    FEATURED_MODELS = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-haiku",
        "openai/gpt-4-turbo",
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "google/gemini-pro-1.5",
        "meta-llama/llama-3.1-70b-instruct",
        "mistralai/mistral-large",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize the OpenRouter service.

        Args:
            api_key: OpenRouter API key. If None, uses settings.
            base_url: Base URL for API. If None, uses settings.
        """
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-across.local",
            "X-Title": "AI-Across",
        }

    async def list_models(self) -> list[dict[str, Any]]:
        """List available models from OpenRouter.

        Returns:
            List of model dictionaries with id, name, context_length, and pricing.

        Raises:
            OpenRouterError: If API request fails.
        """
        if not self.api_key:
            raise OpenRouterError("OpenRouter API key not configured")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._get_headers(),
                )
                response.raise_for_status()

                data = response.json()
                models = data.get("data", [])

                # Transform to our format and filter for chat models
                result = []
                for model in models:
                    model_info = {
                        "id": model.get("id", ""),
                        "name": model.get("name", model.get("id", "")),
                        "description": model.get("description"),
                        "context_length": model.get("context_length", 4096),
                        "pricing": {
                            "prompt": model.get("pricing", {}).get("prompt", "0"),
                            "completion": model.get("pricing", {}).get("completion", "0"),
                        },
                    }
                    result.append(model_info)

                # Sort: featured models first, then alphabetically
                def sort_key(m):
                    is_featured = m["id"] in self.FEATURED_MODELS
                    featured_index = (
                        self.FEATURED_MODELS.index(m["id"])
                        if is_featured
                        else len(self.FEATURED_MODELS)
                    )
                    return (not is_featured, featured_index, m["id"])

                result.sort(key=sort_key)

                return result

            except httpx.HTTPStatusError as e:
                raise OpenRouterError(
                    f"Failed to fetch models: {e.response.text}",
                    status_code=e.response.status_code,
                )
            except Exception as e:
                raise OpenRouterError(f"Failed to fetch models: {str(e)}")

    async def get_model_pricing(self, model_id: str) -> dict[str, float]:
        """Get pricing for a specific model.

        Pricing is cached for 24 hours to reduce API calls.

        Args:
            model_id: The model ID to get pricing for.

        Returns:
            Dictionary with 'prompt' and 'completion' prices in USD per 1M tokens.
        """
        global _pricing_cache, _pricing_cache_time

        # Check if cache is valid
        current_time = time.time()
        if not _pricing_cache or (current_time - _pricing_cache_time) > _PRICING_CACHE_TTL:
            # Refresh cache
            try:
                models = await self.list_models()
                _pricing_cache = {}
                for model in models:
                    pricing = model.get("pricing", {})
                    _pricing_cache[model["id"]] = {
                        "prompt": float(pricing.get("prompt", 0)),
                        "completion": float(pricing.get("completion", 0)),
                    }
                _pricing_cache_time = current_time
            except Exception:
                # If we can't fetch, return zeros
                if model_id not in _pricing_cache:
                    return {"prompt": 0.0, "completion": 0.0}

        return _pricing_cache.get(model_id, {"prompt": 0.0, "completion": 0.0})

    async def check_connectivity(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Check connectivity to OpenRouter API.

        Returns:
            Tuple of (is_connected, latency_ms, error_message).
        """
        if not self.api_key:
            return False, None, "API key not configured"

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._get_headers(),
                )

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                return True, latency_ms, None
            elif response.status_code == 401:
                return False, latency_ms, "Invalid API key"
            else:
                return False, latency_ms, f"HTTP {response.status_code}"

        except httpx.TimeoutException:
            return False, None, "Connection timeout"
        except Exception as e:
            return False, None, str(e)

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Create a chat completion (non-streaming).

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model ID to use. Defaults to settings.default_model.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.
            stream: Whether to stream the response (use stream_chat_completion for streaming).

        Returns:
            Completion response with content and usage information.

        Raises:
            OpenRouterError: If API request fails.
        """
        if not self.api_key:
            raise OpenRouterError("OpenRouter API key not configured")

        model = model or settings.default_model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        start_time = time.time()
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                latency_ms = int((time.time() - start_time) * 1000)
                tokens = data.get("usage", {})
                logger.info(
                    "Chat completion finished",
                    extra={
                        "model": model,
                        "latency_ms": latency_ms,
                        "prompt_tokens": tokens.get("prompt_tokens", 0),
                        "completion_tokens": tokens.get("completion_tokens", 0),
                        "total_tokens": tokens.get("total_tokens", 0),
                    },
                )
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": data.get("model", model),
                    "tokens_used": {
                        "prompt_tokens": tokens.get("prompt_tokens", 0),
                        "completion_tokens": tokens.get("completion_tokens", 0),
                        "total_tokens": tokens.get("total_tokens", 0),
                    },
                }

            except httpx.HTTPStatusError as e:
                latency_ms = int((time.time() - start_time) * 1000)
                logger.error(
                    "Chat completion HTTP error",
                    extra={"model": model, "latency_ms": latency_ms, "status_code": e.response.status_code},
                )
                raise OpenRouterError(
                    f"Chat completion failed: {e.response.text}",
                    status_code=e.response.status_code,
                )
            except Exception as e:
                logger.error("Chat completion error", extra={"model": model, "error": str(e)})
                raise OpenRouterError(f"Chat completion failed: {str(e)}")

    async def stream_chat_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[dict[str, Any]]:
        """Create a streaming chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model ID to use. Defaults to settings.default_model.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.

        Yields:
            Streaming chunks with type and content.

        Raises:
            OpenRouterError: If API request fails.
        """
        if not self.api_key:
            raise OpenRouterError("OpenRouter API key not configured")

        model = model or settings.default_model

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        start_time = time.time()
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        logger.error(
                            "Streaming completion HTTP error",
                            extra={"model": model, "status_code": response.status_code},
                        )
                        raise OpenRouterError(
                            f"Chat completion failed: {error_body.decode()}",
                            status_code=response.status_code,
                        )

                    accumulated_content = ""
                    prompt_tokens = 0
                    completion_tokens = 0

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        if line.startswith("data: "):
                            data_str = line[6:]

                            if data_str.strip() == "[DONE]":
                                latency_ms = int((time.time() - start_time) * 1000)
                                logger.info(
                                    "Streaming completion finished",
                                    extra={
                                        "model": model,
                                        "latency_ms": latency_ms,
                                        "prompt_tokens": prompt_tokens,
                                        "completion_tokens": completion_tokens,
                                        "total_tokens": prompt_tokens + completion_tokens,
                                    },
                                )
                                # Stream complete
                                yield {
                                    "type": "done",
                                    "content": accumulated_content,
                                    "tokens_used": {
                                        "prompt_tokens": prompt_tokens,
                                        "completion_tokens": completion_tokens,
                                        "total_tokens": prompt_tokens + completion_tokens,
                                    },
                                }
                                break

                            try:
                                data = json.loads(data_str)

                                # Extract content from delta
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")

                                    if content:
                                        accumulated_content += content
                                        yield {
                                            "type": "content",
                                            "content": content,
                                        }

                                # Extract usage if present (some providers include it)
                                usage = data.get("usage", {})
                                if usage:
                                    prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
                                    completion_tokens = usage.get(
                                        "completion_tokens", completion_tokens
                                    )

                            except json.JSONDecodeError:
                                # Skip malformed JSON
                                continue

            except httpx.HTTPStatusError as e:
                yield {
                    "type": "error",
                    "error": f"Chat completion failed: {e.response.text}",
                }
            except OpenRouterError:
                raise
            except Exception as e:
                yield {
                    "type": "error",
                    "error": f"Chat completion failed: {str(e)}",
                }


def get_openrouter_service(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> OpenRouterService:
    """Get an OpenRouter service instance.

    Args:
        api_key: Optional API key override.
        base_url: Optional base URL override.

    Returns:
        OpenRouterService instance.
    """
    return OpenRouterService(api_key=api_key, base_url=base_url)
