"""Pydantic schemas for Conversation and Message API."""

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base schema for Message."""

    content: str = Field(..., min_length=1, max_length=100000)


class MessageCreate(MessageBase):
    """Schema for creating a new message (user sends to chat)."""

    pass


class MessageUpdate(BaseModel):
    """Schema for updating an existing message."""

    content: str = Field(..., min_length=1, max_length=100000)


class MessageResponse(MessageBase):
    """Schema for Message API response."""

    id: UUID
    conversation_id: UUID
    role: str
    model: Optional[str] = None
    tokens_used: Optional[dict[str, Any]] = None
    created_at: datetime
    feedback: Optional[str] = None
    feedback_reason: Optional[str] = None

    model_config = {"from_attributes": True}


class FeedbackCreate(BaseModel):
    """Schema for submitting message feedback."""

    feedback: Literal["positive", "negative"]
    reason: Optional[str] = Field(default=None, max_length=1000)


class ConversationBase(BaseModel):
    """Base schema for Conversation."""

    title: str = Field(default="New Conversation", max_length=200)


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""

    assistant_id: UUID


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: Optional[str] = Field(default=None, max_length=200)


class ConversationResponse(ConversationBase):
    """Schema for Conversation API response."""

    id: UUID
    assistant_id: Optional[UUID] = None
    message_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailResponse(ConversationResponse):
    """Schema for Conversation detail response with messages."""

    messages: list[MessageResponse] = Field(default_factory=list)


class ConversationListResponse(BaseModel):
    """Schema for list of conversations response."""

    conversations: list[ConversationResponse]
    total: int


class ConversationExport(BaseModel):
    """Schema for exported conversation."""

    id: UUID
    title: str
    assistant_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]


class StreamingChunk(BaseModel):
    """Schema for a streaming response chunk."""

    type: str  # "content", "done", "error"
    content: Optional[str] = None
    message_id: Optional[UUID] = None
    tokens_used: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class ChatRequest(MessageCreate):
    """Schema for chat request with additional options."""

    model: Optional[str] = Field(default=None, max_length=100)


class ModelInfo(BaseModel):
    """Schema for model information."""

    id: str
    name: str
    description: Optional[str] = None
    context_length: int
    pricing: Optional[dict[str, Any]] = None


class ModelsListResponse(BaseModel):
    """Schema for list of models response."""

    models: list[ModelInfo]
