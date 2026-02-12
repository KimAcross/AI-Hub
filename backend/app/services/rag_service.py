"""RAG (Retrieval-Augmented Generation) service for context retrieval."""

import uuid
from dataclasses import dataclass
from typing import Optional

from app.services.chroma_service import ChromaService, get_chroma_service
from app.services.embedding_service import EmbeddingService, get_embedding_service


@dataclass
class RetrievedChunk:
    """Represents a retrieved chunk with its relevance score."""

    text: str
    score: float
    file_id: str
    chunk_index: int
    metadata: dict


class RAGService:
    """Service for RAG-based context retrieval."""

    # Default prompt template for RAG context injection
    RAG_PROMPT_TEMPLATE = """You are {assistant_name}.

{assistant_instructions}

Use the following reference materials to inform your response. Only use information from these materials when relevant:

---
{retrieved_chunks}
---

If the reference materials don't contain relevant information, rely on your general knowledge but indicate this to the user."""

    def __init__(
        self,
        chroma_service: Optional[ChromaService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ):
        """Initialize the RAG service.

        Args:
            chroma_service: ChromaDB service for vector storage.
            embedding_service: Service for generating embeddings.
            top_k: Number of top results to retrieve.
            similarity_threshold: Minimum similarity score (0-1) for results.
        """
        self.chroma_service = chroma_service or get_chroma_service()
        self.embedding_service = embedding_service or get_embedding_service()
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    async def retrieve(
        self,
        assistant_id: uuid.UUID,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant chunks for a query.

        Args:
            assistant_id: UUID of the assistant.
            query: Query text to find relevant chunks for.
            top_k: Number of results to return (overrides default).
            threshold: Similarity threshold (overrides default).

        Returns:
            List of RetrievedChunk objects sorted by relevance.
        """
        k = top_k if top_k is not None else self.top_k
        min_threshold = threshold if threshold is not None else self.similarity_threshold

        # Generate embedding for the query
        query_embedding = await self.embedding_service.embed_text(query)

        # Query ChromaDB
        results = self.chroma_service.query(
            assistant_id=assistant_id,
            query_embedding=query_embedding,
            n_results=k,
        )

        # Convert distances to similarity scores (ChromaDB uses L2 distance by default)
        # For cosine similarity: similarity = 1 - (distance / 2)
        # For L2 distance with normalized vectors: similarity = 1 - (distance^2 / 2)
        chunks: list[RetrievedChunk] = []

        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        distances = results.get("distances", [])

        for i, (doc, metadata, distance) in enumerate(
            zip(documents, metadatas, distances)
        ):
            # Convert L2 distance to similarity score
            # Assuming embeddings are normalized, distance is between 0 and 2
            similarity = 1 - (distance / 2)

            if similarity >= min_threshold:
                chunks.append(
                    RetrievedChunk(
                        text=doc,
                        score=similarity,
                        file_id=metadata.get("file_id", ""),
                        chunk_index=metadata.get("chunk_index", i),
                        metadata=metadata,
                    )
                )

        # Sort by score descending
        chunks.sort(key=lambda x: x.score, reverse=True)

        return chunks

    def format_context(
        self,
        chunks: list[RetrievedChunk],
        max_tokens: int = 4000,
    ) -> str:
        """Format retrieved chunks as context for the LLM.

        Args:
            chunks: List of retrieved chunks.
            max_tokens: Maximum approximate tokens for context.

        Returns:
            Formatted context string.
        """
        if not chunks:
            return ""

        context_parts: list[str] = []
        total_chars = 0
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4

        for i, chunk in enumerate(chunks, 1):
            chunk_text = f"[Source {i}]\n{chunk.text}"

            if total_chars + len(chunk_text) > max_chars:
                # Stop adding chunks if we exceed the limit
                break

            context_parts.append(chunk_text)
            total_chars += len(chunk_text) + 2  # +2 for newlines

        return "\n\n".join(context_parts)

    def build_system_prompt(
        self,
        assistant_name: str,
        assistant_instructions: str,
        context: str,
    ) -> str:
        """Build the system prompt with RAG context.

        Args:
            assistant_name: Name of the assistant.
            assistant_instructions: Original assistant instructions.
            context: Formatted context from retrieved chunks.

        Returns:
            Complete system prompt with context.
        """
        if not context:
            # No context, return simple prompt
            return f"You are {assistant_name}.\n\n{assistant_instructions}"

        return self.RAG_PROMPT_TEMPLATE.format(
            assistant_name=assistant_name,
            assistant_instructions=assistant_instructions,
            retrieved_chunks=context,
        )

    async def get_augmented_prompt(
        self,
        assistant_id: uuid.UUID,
        assistant_name: str,
        assistant_instructions: str,
        user_query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        max_context_tokens: Optional[int] = None,
    ) -> tuple[str, list[RetrievedChunk]]:
        """Get a system prompt augmented with relevant context.

        Args:
            assistant_id: UUID of the assistant.
            assistant_name: Name of the assistant.
            assistant_instructions: Original assistant instructions.
            user_query: The user's query to find context for.
            top_k: Number of results to retrieve.
            threshold: Similarity threshold.
            max_context_tokens: Maximum tokens for context (per-assistant override).

        Returns:
            Tuple of (augmented system prompt, list of retrieved chunks).
        """
        # Retrieve relevant chunks
        chunks = await self.retrieve(
            assistant_id=assistant_id,
            query=user_query,
            top_k=top_k,
            threshold=threshold,
        )

        # Format the context with per-assistant token limit
        context_limit = max_context_tokens if max_context_tokens is not None else 4000
        context = self.format_context(chunks, max_tokens=context_limit)

        # Build the system prompt
        system_prompt = self.build_system_prompt(
            assistant_name=assistant_name,
            assistant_instructions=assistant_instructions,
            context=context,
        )

        return system_prompt, chunks


# Default service factory
def get_rag_service(
    top_k: int = 5,
    similarity_threshold: float = 0.7,
) -> RAGService:
    """Get a RAG service instance.

    Args:
        top_k: Number of top results to retrieve.
        similarity_threshold: Minimum similarity score for results.

    Returns:
        RAGService instance.
    """
    return RAGService(top_k=top_k, similarity_threshold=similarity_threshold)
