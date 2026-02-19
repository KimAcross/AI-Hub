"""Background reaper for resilient file ingestion retries."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.knowledge_file import KnowledgeFile
from app.services.file_processor import FileProcessorService

logger = get_logger(__name__)
settings = get_settings()

BACKOFF_MINUTES = (5, 15, 45)


class IngestionReaper:
    """Find and recover stuck/pending ingestion records."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.processor = FileProcessorService(db)

    async def run_once(self) -> None:
        """Run one full retry pass."""
        await self._recover_stale_processing()
        await self._process_due_retries()

    async def _recover_stale_processing(self) -> None:
        now = datetime.now(timezone.utc)
        stale_cutoff = now - timedelta(
            minutes=settings.ingestion_stale_processing_minutes
        )

        result = await self.db.execute(
            select(KnowledgeFile).where(
                and_(
                    KnowledgeFile.status.in_(["processing", "indexing"]),
                    or_(
                        KnowledgeFile.processing_started_at < stale_cutoff,
                        and_(
                            KnowledgeFile.processing_started_at.is_(None),
                            KnowledgeFile.created_at < stale_cutoff,
                        ),
                    ),
                )
            )
        )
        stale_files = list(result.scalars().all())

        for file in stale_files:
            await self._schedule_retry(file, reason="stale_processing")

    async def _process_due_retries(self) -> None:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(KnowledgeFile).where(
                and_(
                    KnowledgeFile.status == "pending",
                    KnowledgeFile.next_retry_at.is_not(None),
                    KnowledgeFile.next_retry_at <= now,
                )
            )
        )
        files = list(result.scalars().all())

        for file in files:
            await self.processor.process_file(file.id)

    async def _schedule_retry(self, file: KnowledgeFile, reason: str) -> None:
        if file.attempt_count >= file.max_attempts:
            file.status = "failed"
            file.last_error = (
                file.last_error
                or f"Exceeded max attempts ({file.max_attempts}) due to {reason}"
            )
            logger.warning(
                "ingestion_failed_max_attempts",
                extra={
                    "file_id": str(file.id),
                    "assistant_id": str(file.assistant_id),
                    "attempt_count": file.attempt_count,
                    "max_attempts": file.max_attempts,
                },
            )
            return

        next_attempt_number = file.attempt_count + 1
        backoff_index = min(next_attempt_number - 1, len(BACKOFF_MINUTES) - 1)
        next_retry_at = datetime.now(timezone.utc) + timedelta(
            minutes=BACKOFF_MINUTES[backoff_index]
        )

        file.status = "pending"
        file.next_retry_at = next_retry_at
        file.last_error = f"Retry scheduled ({reason}), attempt {next_attempt_number}"

        logger.info(
            "ingestion_retry_scheduled",
            extra={
                "file_id": str(file.id),
                "assistant_id": str(file.assistant_id),
                "attempt_count": file.attempt_count,
                "next_retry_at": next_retry_at.isoformat(),
            },
        )
