"""Text chunking utilities for RAG pipeline."""

import tiktoken
from dataclasses import dataclass


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""

    text: str
    index: int
    token_count: int


class TextChunker:
    """Chunk text into smaller pieces for embedding.

    Uses tiktoken for accurate token counting with the cl100k_base encoding
    (used by text-embedding-3-small and most modern OpenAI models).
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base",
    ):
        """Initialize the chunker.

        Args:
            chunk_size: Maximum number of tokens per chunk.
            chunk_overlap: Number of overlapping tokens between chunks.
            encoding_name: Name of the tiktoken encoding to use.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens.
        """
        return len(self.encoding.encode(text))

    def chunk_text(self, text: str) -> list[TextChunk]:
        """Split text into overlapping chunks based on token count.

        Args:
            text: Text to chunk.

        Returns:
            List of TextChunk objects.
        """
        # Normalize whitespace
        text = " ".join(text.split())

        if not text:
            return []

        # Encode the entire text
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)

        if total_tokens <= self.chunk_size:
            # Text fits in a single chunk
            return [
                TextChunk(
                    text=text,
                    index=0,
                    token_count=total_tokens,
                )
            ]

        chunks: list[TextChunk] = []
        start = 0
        index = 0

        while start < total_tokens:
            # Calculate end position
            end = min(start + self.chunk_size, total_tokens)

            # Extract tokens for this chunk
            chunk_tokens = tokens[start:end]

            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)

            chunks.append(
                TextChunk(
                    text=chunk_text.strip(),
                    index=index,
                    token_count=len(chunk_tokens),
                )
            )

            # Move start position, accounting for overlap
            start = end - self.chunk_overlap
            index += 1

            # Prevent infinite loop if overlap >= chunk_size
            if start >= total_tokens:
                break

        return chunks


# Default chunker instance
default_chunker = TextChunker()


def chunk_text(text: str) -> list[TextChunk]:
    """Chunk text using the default chunker.

    Args:
        text: Text to chunk.

    Returns:
        List of TextChunk objects.
    """
    return default_chunker.chunk_text(text)
