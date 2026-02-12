"""File management API endpoints."""

import uuid
from typing import Annotated

from app.core.logging import get_logger

logger = get_logger(__name__)

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_assistant_service, require_admin_role, require_any_role
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.file import FileListResponse, FileResponse, FileUploadResponse
from app.services.assistant_service import AssistantService
from app.services.file_processor import FileProcessorService


router = APIRouter(prefix="/assistants/{assistant_id}/files", tags=["files"])


async def get_file_processor(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> FileProcessorService:
    """Dependency that provides a FileProcessorService instance."""
    return FileProcessorService(db)


async def process_file_background(
    file_id: uuid.UUID,
    db_url: str,
) -> None:
    """Background task to process a file.

    Creates a new database session for background processing.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            processor = FileProcessorService(session)
            await processor.process_file(file_id)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error processing file {file_id}: {e}")
        finally:
            await session.close()

    await engine.dispose()


@router.post(
    "",
    response_model=FileUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a file to assistant's knowledge base",
    description="Upload a PDF, DOCX, TXT, or MD file. The file will be processed asynchronously.",
)
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    assistant_id: uuid.UUID,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
    file_processor: Annotated[FileProcessorService, Depends(get_file_processor)],
    _auth: dict = Depends(require_admin_role),
) -> FileUploadResponse:
    """Upload a file to an assistant's knowledge base.

    The file will be validated, saved, and queued for background processing.
    Processing includes text extraction, chunking, embedding generation,
    and vector storage.
    """
    # Verify assistant exists
    assistant = await assistant_service.get_assistant(assistant_id)
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found",
        )

    try:
        # Upload and create file record
        knowledge_file = await file_processor.upload_and_process(
            file=file,
            assistant_id=assistant_id,
        )

        # Queue background processing
        from app.core.config import get_settings
        settings = get_settings()

        background_tasks.add_task(
            process_file_background,
            knowledge_file.id,
            settings.database_url,
        )

        return FileUploadResponse(
            id=knowledge_file.id,
            filename=knowledge_file.filename,
            status=knowledge_file.status,
            assistant_id=knowledge_file.assistant_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=FileListResponse,
    summary="List all files for an assistant",
)
async def list_files(
    assistant_id: uuid.UUID,
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
    file_processor: Annotated[FileProcessorService, Depends(get_file_processor)],
    _auth: dict = Depends(require_any_role),
) -> FileListResponse:
    """Get all files uploaded to an assistant's knowledge base."""
    # Verify assistant exists
    assistant = await assistant_service.get_assistant(assistant_id)
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found",
        )

    files = await file_processor.get_assistant_files(assistant_id)

    return FileListResponse(
        files=[FileResponse.model_validate(f) for f in files],
        total=len(files),
    )


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    summary="Get file details",
)
async def get_file(
    assistant_id: uuid.UUID,
    file_id: uuid.UUID,
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
    file_processor: Annotated[FileProcessorService, Depends(get_file_processor)],
    _auth: dict = Depends(require_any_role),
) -> FileResponse:
    """Get details of a specific file."""
    # Verify assistant exists
    assistant = await assistant_service.get_assistant(assistant_id)
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found",
        )

    file = await file_processor.get_file(file_id)

    if not file or file.assistant_id != assistant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    return FileResponse.model_validate(file)


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a file",
)
async def delete_file(
    assistant_id: uuid.UUID,
    file_id: uuid.UUID,
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
    file_processor: Annotated[FileProcessorService, Depends(get_file_processor)],
    _auth: dict = Depends(require_admin_role),
) -> None:
    """Delete a file from an assistant's knowledge base.

    This will remove the file, its database record, and all associated
    vector embeddings from ChromaDB.
    """
    # Verify assistant exists
    assistant = await assistant_service.get_assistant(assistant_id)
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found",
        )

    # Verify file exists and belongs to assistant
    file = await file_processor.get_file(file_id)
    if not file or file.assistant_id != assistant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    await file_processor.delete_file(file_id)


@router.post(
    "/{file_id}/reprocess",
    response_model=FileResponse,
    summary="Reprocess a file",
    description="Reprocess a file that failed processing or needs to be re-indexed.",
)
async def reprocess_file(
    assistant_id: uuid.UUID,
    file_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
    file_processor: Annotated[FileProcessorService, Depends(get_file_processor)],
    _auth: dict = Depends(require_admin_role),
) -> FileResponse:
    """Reprocess a file.

    Useful for files that failed during initial processing or when
    the embedding model has been updated.
    """
    # Verify assistant exists
    assistant = await assistant_service.get_assistant(assistant_id)
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found",
        )

    # Verify file exists and belongs to assistant
    file = await file_processor.get_file(file_id)
    if not file or file.assistant_id != assistant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    # Start reprocessing
    await file_processor.reprocess_file(file_id)

    # Refresh file to get updated status
    file = await file_processor.get_file(file_id)

    # Queue background processing
    from app.core.config import get_settings
    settings = get_settings()

    background_tasks.add_task(
        process_file_background,
        file_id,
        settings.database_url,
    )

    return FileResponse.model_validate(file)
