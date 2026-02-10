"""ChromaDB service for vector storage and retrieval."""

import uuid
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings


settings = get_settings()


class ChromaService:
    """Service for managing ChromaDB vector storage."""

    _instance: Optional["ChromaService"] = None
    _client: Optional[chromadb.ClientAPI] = None

    def __new__(cls) -> "ChromaService":
        """Singleton pattern to ensure single ChromaDB client."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize ChromaDB client with persistent storage."""
        if self._client is not None:
            return

        # Ensure persist directory exists
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize persistent client
        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

    @property
    def client(self) -> chromadb.ClientAPI:
        """Get the ChromaDB client."""
        if self._client is None:
            raise RuntimeError("ChromaDB client not initialized")
        return self._client

    def get_collection_name(self, assistant_id: uuid.UUID) -> str:
        """Get the collection name for an assistant.

        Args:
            assistant_id: UUID of the assistant.

        Returns:
            Collection name string.
        """
        return f"assistant_{str(assistant_id).replace('-', '_')}"

    def get_or_create_collection(
        self,
        assistant_id: uuid.UUID,
    ) -> chromadb.Collection:
        """Get or create a collection for an assistant.

        Args:
            assistant_id: UUID of the assistant.

        Returns:
            ChromaDB collection.
        """
        collection_name = self.get_collection_name(assistant_id)
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"assistant_id": str(assistant_id)},
        )

    def add_chunks(
        self,
        assistant_id: uuid.UUID,
        file_id: uuid.UUID,
        chunks: list[str],
        embeddings: list[list[float]],
        metadatas: Optional[list[dict]] = None,
    ) -> int:
        """Add text chunks with embeddings to a collection.

        Args:
            assistant_id: UUID of the assistant.
            file_id: UUID of the file the chunks came from.
            chunks: List of text chunks.
            embeddings: List of embedding vectors.
            metadatas: Optional list of metadata dicts for each chunk.

        Returns:
            Number of chunks added.
        """
        if not chunks or not embeddings:
            return 0

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        collection = self.get_or_create_collection(assistant_id)

        # Generate unique IDs for each chunk
        ids = [
            f"{file_id}_{i}"
            for i in range(len(chunks))
        ]

        # Build metadata for each chunk
        if metadatas is None:
            metadatas = [{} for _ in chunks]

        for i, metadata in enumerate(metadatas):
            metadata["file_id"] = str(file_id)
            metadata["chunk_index"] = i

        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    def query(
        self,
        assistant_id: uuid.UUID,
        query_embedding: list[float],
        n_results: int = 5,
        where: Optional[dict] = None,
    ) -> dict:
        """Query the collection for similar chunks.

        Args:
            assistant_id: UUID of the assistant.
            query_embedding: Embedding vector for the query.
            n_results: Number of results to return.
            where: Optional filter conditions.

        Returns:
            Query results with documents, metadatas, and distances.
        """
        collection = self.get_or_create_collection(assistant_id)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        return {
            "documents": results.get("documents", [[]])[0],
            "metadatas": results.get("metadatas", [[]])[0],
            "distances": results.get("distances", [[]])[0],
        }

    def delete_file_chunks(
        self,
        assistant_id: uuid.UUID,
        file_id: uuid.UUID,
    ) -> None:
        """Delete all chunks for a specific file.

        Args:
            assistant_id: UUID of the assistant.
            file_id: UUID of the file.
        """
        collection = self.get_or_create_collection(assistant_id)

        # Delete by file_id metadata filter
        collection.delete(
            where={"file_id": str(file_id)},
        )

    def delete_collection(self, assistant_id: uuid.UUID) -> None:
        """Delete the entire collection for an assistant.

        Args:
            assistant_id: UUID of the assistant.
        """
        collection_name = self.get_collection_name(assistant_id)
        try:
            self.client.delete_collection(collection_name)
        except ValueError:
            # Collection doesn't exist, ignore
            pass

    def get_collection_count(self, assistant_id: uuid.UUID) -> int:
        """Get the number of documents in a collection.

        Args:
            assistant_id: UUID of the assistant.

        Returns:
            Number of documents in the collection.
        """
        collection = self.get_or_create_collection(assistant_id)
        return collection.count()


# Singleton instance
chroma_service = ChromaService()


def get_chroma_service() -> ChromaService:
    """Get the ChromaDB service singleton."""
    return chroma_service
