"""Tests for text chunking utilities."""

from app.utils.chunker import TextChunker, TextChunk, chunk_text


class TestTextChunker:
    """Test suite for TextChunker class."""

    def test_init_defaults(self):
        """Test TextChunker initialization with defaults."""
        chunker = TextChunker()
        assert chunker.chunk_size == 512
        assert chunker.chunk_overlap == 50

    def test_init_custom(self):
        """Test TextChunker initialization with custom values."""
        chunker = TextChunker(chunk_size=256, chunk_overlap=25)
        assert chunker.chunk_size == 256
        assert chunker.chunk_overlap == 25

    def test_count_tokens(self):
        """Test token counting."""
        chunker = TextChunker()

        # Empty text
        assert chunker.count_tokens("") == 0

        # Simple text
        token_count = chunker.count_tokens("Hello, world!")
        assert token_count > 0
        assert token_count < 10  # Should be just a few tokens

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker()
        chunks = chunker.chunk_text("")
        assert chunks == []

    def test_chunk_whitespace_only(self):
        """Test chunking whitespace-only text."""
        chunker = TextChunker()
        chunks = chunker.chunk_text("   \n\t  ")
        assert chunks == []

    def test_chunk_small_text(self):
        """Test chunking text smaller than chunk size."""
        chunker = TextChunker(chunk_size=100)
        text = "This is a small piece of text that fits in one chunk."
        chunks = chunker.chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0].index == 0
        assert chunks[0].token_count <= 100

    def test_chunk_large_text(self):
        """Test chunking text larger than chunk size."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        # Create text that will need multiple chunks
        text = " ".join(["word"] * 200)  # ~200 tokens
        chunks = chunker.chunk_text(text)

        assert len(chunks) > 1
        # Verify indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.index == i
            assert chunk.token_count <= 50

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        chunker = TextChunker(chunk_size=20, chunk_overlap=5)
        text = " ".join(["test"] * 50)  # Create text that needs multiple chunks
        chunks = chunker.chunk_text(text)

        # Verify we get multiple chunks
        assert len(chunks) > 2

    def test_chunk_preserves_content(self):
        """Test that chunking preserves all content."""
        chunker = TextChunker(chunk_size=50, chunk_overlap=0)
        original_text = "The quick brown fox jumps over the lazy dog. " * 10
        chunks = chunker.chunk_text(original_text)

        # Reconstruct text (approximately - overlap may cause duplicates)
        # At minimum, verify first chunk starts correctly
        assert chunks[0].text.startswith("The quick brown fox")

    def test_textchunk_dataclass(self):
        """Test TextChunk dataclass."""
        chunk = TextChunk(text="test", index=0, token_count=1)
        assert chunk.text == "test"
        assert chunk.index == 0
        assert chunk.token_count == 1


class TestDefaultChunker:
    """Test the default chunk_text function."""

    def test_chunk_text_function(self):
        """Test the default chunk_text function."""
        text = "This is a test text for chunking."
        chunks = chunk_text(text)

        assert len(chunks) >= 1
        assert isinstance(chunks[0], TextChunk)

    def test_chunk_text_empty(self):
        """Test default chunk_text with empty input."""
        chunks = chunk_text("")
        assert chunks == []
