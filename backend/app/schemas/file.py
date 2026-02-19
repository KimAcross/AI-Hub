"""Pydantic schemas for file operations."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FileBase(BaseModel):
    """Base schema for file attributes."""

    filename: str = Field(..., min_length=1, max_length=255)


class FileCreate(FileBase):
    """Schema for creating a file (internal use)."""

    file_type: str = Field(..., max_length=20)
    file_path: str = Field(..., max_length=500)
    size_bytes: int = Field(..., gt=0)
    assistant_id: uuid.UUID


class FileResponse(BaseModel):
    """Schema for file response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assistant_id: uuid.UUID
    filename: str
    file_type: str
    size_bytes: int
    chunk_count: int
    status: str
    error_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    attempt_count: int = 0
    max_attempts: int = 3
    next_retry_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime


class FileListResponse(BaseModel):
    """Schema for listing files."""

    files: list[FileResponse]
    total: int


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""

    id: uuid.UUID
    filename: str
    status: str
    assistant_id: uuid.UUID


class FileStatusUpdate(BaseModel):
    """Schema for updating file status (internal use)."""

    status: str
    chunk_count: Optional[int] = None
    error_message: Optional[str] = None
