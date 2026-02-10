"""Embedding service for generating text embeddings via OpenRouter."""

import asyncio
from typing import Optional

import httpx

from app.core.config import get_settings


settings = get_settings()


class EmbeddingService:
    """Service for generating text embeddings using OpenRouter's API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        batch_size: int = 100,
    ):
        """Initialize the embedding service.

        Args:
            api_key: OpenRouter API key. If None, uses settings.
            model: Embedding model to use. If None, uses settings.
            batch_size: Maximum number of texts to embed in one request.
        """
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.embedding_model
        self.batch_size = batch_size
        self.base_url = settings.openrouter_base_url

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as list of floats.

        Raises:
            ValueError: If API key is not configured.
            httpx.HTTPStatusError: If API request fails.
        """
        embeddings = await self.embed_texts([text])
        return embeddings[0]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Handles batching automatically if texts exceed batch_size.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.

        Raises:
            ValueError: If API key is not configured.
            httpx.HTTPStatusError: If API request fails.
        """
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not configured. "
                "Set OPENROUTER_API_KEY environment variable."
            )

        if not texts:
            return []

        # Process in batches
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_embeddings = await self._embed_batch(batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    async def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts.

        Args:
            texts: Batch of texts to embed.

        Returns:
            List of embedding vectors.
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ai-across.local",
                    "X-Title": "AI-Across",
                },
                json={
                    "model": self.model,
                    "input": texts,
                },
            )
            response.raise_for_status()

            data = response.json()
            # Sort by index to ensure order is preserved
            embeddings_data = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in embeddings_data]


# Default service instance factory
def get_embedding_service(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> EmbeddingService:
    """Get an embedding service instance.

    Args:
        api_key: Optional API key override.
        model: Optional model override.

    Returns:
        EmbeddingService instance.
    """
    return EmbeddingService(api_key=api_key, model=model)
