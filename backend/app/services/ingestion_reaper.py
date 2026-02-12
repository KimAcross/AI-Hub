"""Ingestion reaper: periodic task that detects and retries stuck file processing."""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.knowledge_file import KnowledgeFile

logger = get_logger(__name__)

# Backoff multipliers: attempt 1 → 5min, attempt 2 → 15min, attempt 3 → 45min
BACKOFF_BASE_MINUTES = 5
BACKOFF_MULTIPLIER = 3

# A file stuck in "processing" longer than this is considered stuck
STUCK_THRESHOLD_MINUTES = 15

# How often the reaper runs
REAPER_INTERVAL_SECONDS = 300  # 5 minutes


class IngestionReaper:
    """Detects stuck file processing and schedules retries with exponential backoff."""

    def __init__(self, database_url: str):
        self._engine = create_async_engine(database_url)
        self._session_factory = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        self._running = False

    async def run(self) -> None:
        """Main loop — runs every REAPER_INTERVAL_SECONDS."""
        self._running = True
        logger.info("Ingestion reaper started", extra={"interval_seconds": REAPER_INTERVAL_SECONDS})

        while self._running:
            try:
                async with self._session_factory() as session:
                    async with session.begin():
                        stuck = await self._reap_stuck_files(session)
                        retried = await self._retry_pending_files(session)
                    if stuck or retried:
                        logger.info(
                            "Reaper cycle complete",
                            extra={"stuck_found": stuck, "retries_triggered": retried},
                        )
            except Exception as e:
                logger.error("Reaper cycle error", extra={"error": str(e)})

            await asyncio.sleep(REAPER_INTERVAL_SECONDS)

    def stop(self) -> None:
        """Signal the reaper to stop after the current cycle."""
        self._running = False

    async def _reap_stuck_files(self, session: AsyncSession) -> int:
        """Find files stuck in 'processing' beyond the threshold and handle them."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=STUCK_THRESHOLD_MINUTES)

        result = await session.execute(
            select(KnowledgeFile).where(
                and_(
                    KnowledgeFile.status == "processing",
                    KnowledgeFile.processing_started_at.isnot(None),
                    KnowledgeFile.processing_started_at < cutoff,
                )
            )
        )
        stuck_files = result.scalars().all()

        for file in stuck_files:
            file.attempt_count += 1

            if file.attempt_count >= file.max_attempts:
                # Max retries exhausted — mark as failed
                file.status = "failed"
                file.last_error = file.last_error or "Processing timed out after max attempts"
                file.next_retry_at = None
                logger.warning(
                    "File failed after max attempts",
                    extra={
                        "file_id": str(file.id),
                        "filename": file.filename,
                        "attempts": file.attempt_count,
                    },
                )
            else:
                # Schedule retry with exponential backoff
                backoff_minutes = BACKOFF_BASE_MINUTES * (BACKOFF_MULTIPLIER ** (file.attempt_count - 1))
                file.next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=backoff_minutes)
                file.status = "pending"
                file.processing_started_at = None
                logger.info(
                    "Scheduling file retry",
                    extra={
                        "file_id": str(file.id),
                        "filename": file.filename,
                        "attempt": file.attempt_count,
                        "retry_in_minutes": backoff_minutes,
                    },
                )

        return len(stuck_files)

    async def _retry_pending_files(self, session: AsyncSession) -> int:
        """Find files due for retry and re-trigger processing."""
        now = datetime.now(timezone.utc)

        result = await session.execute(
            select(KnowledgeFile).where(
                and_(
                    KnowledgeFile.status == "pending",
                    KnowledgeFile.next_retry_at.isnot(None),
                    KnowledgeFile.next_retry_at <= now,
                    KnowledgeFile.attempt_count < KnowledgeFile.max_attempts,
                )
            )
        )
        retry_files = result.scalars().all()

        for file in retry_files:
            file.status = "processing"
            file.processing_started_at = now
            file.next_retry_at = None
            logger.info(
                "Re-triggering file processing",
                extra={
                    "file_id": str(file.id),
                    "filename": file.filename,
                    "attempt": file.attempt_count + 1,
                },
            )
            # Trigger actual processing in background
            asyncio.create_task(self._process_file(file.id))

        return len(retry_files)

    async def _process_file(self, file_id) -> None:
        """Re-process a file using the FileProcessorService."""
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    from app.services.file_processor import FileProcessorService

                    processor = FileProcessorService(db=session)
                    await processor.process_file(file_id)
        except Exception as e:
            logger.error(
                "Reaper-triggered processing failed",
                extra={"file_id": str(file_id), "error": str(e)},
            )


def get_ingestion_reaper() -> IngestionReaper:
    """Create an IngestionReaper instance from settings."""
    settings = get_settings()
    return IngestionReaper(database_url=settings.database_url)
