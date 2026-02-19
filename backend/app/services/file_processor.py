"""File processor service for handling file uploads and indexing."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import aiofiles
import magic
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.knowledge_file import KnowledgeFile
from app.services.chroma_service import ChromaService, get_chroma_service
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.utils.chunker import chunk_text
from app.utils.file_extractors import extract_text, get_file_type, ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_MIME_TYPES = {
    "pdf": ["application/pdf"],
    "docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
    ],
    "txt": ["text/plain"],
    "md": ["text/plain", "text/markdown"],
}


class FileProcessorService:
    """Service for processing uploaded files into the RAG pipeline."""

    def __init__(
        self,
        db: AsyncSession,
        chroma_service: Optional[ChromaService] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        """Initialize the file processor.

        Args:
            db: Database session.
            chroma_service: ChromaDB service for vector storage.
            embedding_service: Service for generating embeddings.
        """
        self.db = db
        self.chroma_service = chroma_service or get_chroma_service()
        self.embedding_service = embedding_service or get_embedding_service()

        # Ensure upload directory exists
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def validate_file(self, file: UploadFile) -> tuple[bool, str]:
        """Validate an uploaded file with extension AND MIME type checks.

        Args:
            file: The uploaded file.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if not file.filename:
            return False, "Filename is required"

        # Check file extension
        file_type = get_file_type(file.filename)
        if not file_type:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            return False, f"File type not allowed. Allowed types: {allowed}"

        # Check file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if size > settings.max_file_size_bytes:
            return False, f"File too large. Maximum size: {settings.max_file_size_mb}MB"

        if size == 0:
            return False, "File is empty"

        # MIME type validation via magic bytes
        header = await file.read(8192)
        await file.seek(0)

        detected_mime = magic.from_buffer(header, mime=True)
        allowed_mimes = ALLOWED_MIME_TYPES.get(file_type, [])

        if detected_mime not in allowed_mimes:
            return False, (
                f"File content does not match extension '.{file_type}'. "
                f"Detected: {detected_mime}"
            )

        return True, ""

    async def save_file(
        self,
        file: UploadFile,
        assistant_id: uuid.UUID,
    ) -> tuple[Path, str, int]:
        """Save an uploaded file to disk.

        Args:
            file: The uploaded file.
            assistant_id: UUID of the assistant.

        Returns:
            Tuple of (file_path, file_type, size_bytes).
        """
        # Create assistant-specific directory
        assistant_dir = self.upload_dir / str(assistant_id)
        assistant_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_type = get_file_type(file.filename) or "unknown"
        unique_name = f"{uuid.uuid4()}.{file_type}"
        file_path = assistant_dir / unique_name

        # Save file
        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return file_path, file_type, len(content)

    async def create_file_record(
        self,
        assistant_id: uuid.UUID,
        workspace_id: Optional[uuid.UUID],
        filename: str,
        file_type: str,
        file_path: Path,
        size_bytes: int,
    ) -> KnowledgeFile:
        """Create a database record for the uploaded file.

        Args:
            assistant_id: UUID of the assistant.
            filename: Original filename.
            file_type: File type (pdf, docx, txt, md).
            file_path: Path where file is saved.
            size_bytes: File size in bytes.

        Returns:
            Created KnowledgeFile model.
        """
        knowledge_file = KnowledgeFile(
            assistant_id=assistant_id,
            workspace_id=workspace_id,
            filename=filename,
            file_type=file_type,
            file_path=str(file_path),
            size_bytes=size_bytes,
            status="processing",
            processing_started_at=datetime.now(timezone.utc),
            attempt_count=0,
            max_attempts=3,
        )

        self.db.add(knowledge_file)
        await self.db.flush()
        await self.db.refresh(knowledge_file)

        return knowledge_file

    async def update_file_status(
        self,
        file_id: uuid.UUID,
        status: str,
        chunk_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Update the status of a file record.

        Args:
            file_id: UUID of the file.
            status: New status.
            chunk_count: Number of chunks created.
            error_message: Error message if failed.
        """
        result = await self.db.execute(
            select(KnowledgeFile).where(KnowledgeFile.id == file_id)
        )
        file = result.scalar_one_or_none()

        if file:
            file.status = status
            if chunk_count is not None:
                file.chunk_count = chunk_count
            if error_message is not None:
                file.error_message = error_message
            await self.db.flush()

    async def _register_attempt(self, file: KnowledgeFile) -> None:
        """Mark a processing attempt start."""
        file.attempt_count += 1
        file.processing_started_at = datetime.now(timezone.utc)
        file.next_retry_at = None
        file.last_error = None
        file.status = "processing"
        await self.db.flush()

    async def _mark_retry_or_failed(self, file: KnowledgeFile, error: str) -> None:
        """Move file to pending retry or terminal failed state."""
        backoff_minutes = [5, 15, 45]
        if file.attempt_count >= file.max_attempts:
            file.status = "failed"
            file.error_message = error
            file.last_error = error
            await self.db.flush()
            return

        delay_idx = min(file.attempt_count - 1, len(backoff_minutes) - 1)
        file.status = "pending"
        file.error_message = error
        file.last_error = error
        file.next_retry_at = datetime.now(timezone.utc) + timedelta(
            minutes=backoff_minutes[delay_idx]
        )
        await self.db.flush()

    async def process_file(self, file_id: uuid.UUID) -> bool:
        """Process a file: extract text, chunk, embed, and store.

        Args:
            file_id: UUID of the file to process.

        Returns:
            True if successful, False otherwise.
        """
        # Get file record
        result = await self.db.execute(
            select(KnowledgeFile).where(KnowledgeFile.id == file_id)
        )
        file = result.scalar_one_or_none()

        if not file:
            return False

        try:
            await self._register_attempt(file)

            # Update status to indexing
            await self.update_file_status(file_id, "indexing")

            # Extract text
            file_path = Path(file.file_path)
            text = extract_text(file_path, file.file_type)

            if not text.strip():
                await self._mark_retry_or_failed(file, "No text content found in file")
                return False

            # Chunk the text
            chunks = chunk_text(text)

            if not chunks:
                await self._mark_retry_or_failed(file, "Failed to create text chunks")
                return False

            # Generate embeddings
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await self.embedding_service.embed_texts(chunk_texts)

            # Store in ChromaDB
            metadatas = [
                {
                    "filename": file.filename,
                    "chunk_index": chunk.index,
                    "token_count": chunk.token_count,
                }
                for chunk in chunks
            ]

            self.chroma_service.add_chunks(
                assistant_id=file.assistant_id,
                file_id=file_id,
                chunks=chunk_texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            # Update status to ready
            await self.update_file_status(file_id, "ready", chunk_count=len(chunks))
            file.next_retry_at = None
            file.last_error = None
            await self.db.flush()

            logger.info(
                "file_processing_succeeded",
                extra={
                    "file_id": str(file_id),
                    "assistant_id": str(file.assistant_id),
                    "attempt_count": file.attempt_count,
                    "chunk_count": len(chunks),
                },
            )

            return True

        except Exception as e:
            error_text = str(e)[:500]
            await self._mark_retry_or_failed(file, error_text)
            logger.exception(
                "file_processing_failed",
                extra={
                    "file_id": str(file_id),
                    "assistant_id": str(file.assistant_id),
                    "attempt_count": file.attempt_count,
                    "max_attempts": file.max_attempts,
                },
            )
            return False

    async def upload_and_process(
        self,
        file: UploadFile,
        assistant_id: uuid.UUID,
        workspace_id: Optional[uuid.UUID] = None,
    ) -> KnowledgeFile:
        """Upload a file and queue it for processing.

        Args:
            file: The uploaded file.
            assistant_id: UUID of the assistant.

        Returns:
            Created KnowledgeFile model.

        Raises:
            ValueError: If file validation fails.
        """
        # Validate file
        is_valid, error = await self.validate_file(file)
        if not is_valid:
            raise ValueError(error)

        # Save file to disk
        file_path, file_type, size_bytes = await self.save_file(file, assistant_id)

        # Create database record
        knowledge_file = await self.create_file_record(
            assistant_id=assistant_id,
            workspace_id=workspace_id,
            filename=file.filename or "unknown",
            file_type=file_type,
            file_path=file_path,
            size_bytes=size_bytes,
        )

        return knowledge_file

    async def get_file(self, file_id: uuid.UUID) -> Optional[KnowledgeFile]:
        """Get a file by ID.

        Args:
            file_id: UUID of the file.

        Returns:
            KnowledgeFile if found, None otherwise.
        """
        result = await self.db.execute(
            select(KnowledgeFile).where(KnowledgeFile.id == file_id)
        )
        return result.scalar_one_or_none()

    async def get_assistant_files(
        self,
        assistant_id: uuid.UUID,
    ) -> list[KnowledgeFile]:
        """Get all files for an assistant.

        Args:
            assistant_id: UUID of the assistant.

        Returns:
            List of KnowledgeFile models.
        """
        result = await self.db.execute(
            select(KnowledgeFile)
            .where(KnowledgeFile.assistant_id == assistant_id)
            .order_by(KnowledgeFile.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_file(self, file_id: uuid.UUID) -> bool:
        """Delete a file and its chunks.

        Args:
            file_id: UUID of the file.

        Returns:
            True if deleted, False if not found.
        """
        result = await self.db.execute(
            select(KnowledgeFile).where(KnowledgeFile.id == file_id)
        )
        file = result.scalar_one_or_none()

        if not file:
            return False

        # Delete chunks from ChromaDB
        self.chroma_service.delete_file_chunks(
            assistant_id=file.assistant_id,
            file_id=file_id,
        )

        # Delete physical file
        file_path = Path(file.file_path)
        if file_path.exists():
            file_path.unlink()

        # Delete database record
        await self.db.delete(file)
        await self.db.flush()

        return True

    async def reprocess_file(self, file_id: uuid.UUID) -> bool:
        """Reprocess a file (useful for failed files).

        Args:
            file_id: UUID of the file.

        Returns:
            True if processing started, False if file not found.
        """
        result = await self.db.execute(
            select(KnowledgeFile).where(KnowledgeFile.id == file_id)
        )
        file = result.scalar_one_or_none()

        if not file:
            return False

        # Delete existing chunks
        self.chroma_service.delete_file_chunks(
            assistant_id=file.assistant_id,
            file_id=file_id,
        )

        # Reset status
        file.status = "pending"
        file.next_retry_at = datetime.now(timezone.utc)
        file.last_error = "Manual reprocess requested"
        await self.db.flush()

        return True
