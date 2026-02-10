"""Conversation API endpoints."""

import json
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_conversation_service, require_any_role
from app.core.rate_limit import limiter
from app.core.exceptions import AssistantNotFoundError, ConversationNotFoundError
from app.models.user import UserRole
from app.schemas.conversation import (
    ChatRequest,
    ConversationCreate,
    ConversationDetailResponse,
    ConversationExport,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    MessageResponse,
    MessageUpdate,
)
from app.services.conversation_service import (
    ConversationService,
    conversation_to_response,
    message_to_response,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _extract_user_context(auth: dict) -> tuple[Optional[UUID], bool]:
    """Extract user_id and is_admin from auth payload."""
    # Legacy admin token
    if auth.get("sub") == "admin":
        return None, True
    user_id_str = auth.get("sub")
    is_admin = auth.get("role") == UserRole.ADMIN.value
    try:
        user_id = UUID(user_id_str) if user_id_str else None
    except (ValueError, TypeError):
        user_id = None
    return user_id, is_admin


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
)
async def create_conversation(
    data: ConversationCreate,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
    auth: dict = Depends(require_any_role),
) -> ConversationResponse:
    """Create a new conversation with an assistant."""
    try:
        user_id, _ = _extract_user_context(auth)
        conversation = await service.create_conversation(data, user_id=user_id)
        return conversation_to_response(conversation)
    except AssistantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "",
    response_model=ConversationListResponse,
    summary="List conversations",
)
async def list_conversations(
    service: Annotated[ConversationService, Depends(get_conversation_service)],
    auth: dict = Depends(require_any_role),
    assistant_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
) -> ConversationListResponse:
    """Get a list of conversations with optional filtering."""
    user_id, is_admin = _extract_user_context(auth)
    conversations, total = await service.list_conversations(
        assistant_id=assistant_id,
        user_id=user_id,
        is_admin=is_admin,
        limit=limit,
        offset=offset,
    )
    return ConversationListResponse(
        conversations=[conversation_to_response(c) for c in conversations],
        total=total,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Get a conversation by ID",
)
async def get_conversation(
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
    auth: dict = Depends(require_any_role),
) -> ConversationDetailResponse:
    """Get details of a specific conversation including all messages."""
    try:
        user_id, is_admin = _extract_user_context(auth)
        conversation = await service.get_conversation(
            conversation_id, user_id=user_id, is_admin=is_admin
        )
        return ConversationDetailResponse(
            id=conversation.id,
            assistant_id=conversation.assistant_id,
            title=conversation.title,
            message_count=len(conversation.messages),
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[message_to_response(m) for m in conversation.messages],
        )
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Update a conversation",
)
async def update_conversation(
    conversation_id: UUID,
    data: ConversationUpdate,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
    auth: dict = Depends(require_any_role),
) -> ConversationResponse:
    """Update a conversation's title or other properties."""
    try:
        user_id, is_admin = _extract_user_context(auth)
        # Verify ownership first
        await service.get_conversation(
            conversation_id, user_id=user_id, is_admin=is_admin
        )
        conversation = await service.update_conversation(conversation_id, data)
        return conversation_to_response(conversation)
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
)
async def delete_conversation(
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
    auth: dict = Depends(require_any_role),
) -> None:
    """Delete a conversation and all its messages."""
    try:
        user_id, is_admin = _extract_user_context(auth)
        # Verify ownership first
        await service.get_conversation(
            conversation_id, user_id=user_id, is_admin=is_admin
        )
        await service.delete_conversation(conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{conversation_id}/messages",
    summary="Send a message and stream response",
    response_class=StreamingResponse,
)
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    conversation_id: UUID,
    data: ChatRequest,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
    auth: dict = Depends(require_any_role),
) -> StreamingResponse:
    """Send a message to the conversation and stream the assistant's response.

    This endpoint uses Server-Sent Events (SSE) to stream the response.
    Each event is a JSON object with the following structure:

    - `{"type": "user_message", "message_id": "..."}` - User message saved
    - `{"type": "assistant_message_start", "message_id": "..."}` - Assistant message started
    - `{"type": "content", "content": "..."}` - Content chunk
    - `{"type": "done", "message_id": "...", "tokens_used": {...}}` - Response complete
    - `{"type": "error", "error": "..."}` - Error occurred
    """
    # Verify ownership before streaming
    user_id, is_admin = _extract_user_context(auth)
    try:
        await service.get_conversation(
            conversation_id, user_id=user_id, is_admin=is_admin
        )
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    async def generate():
        try:
            async for chunk in service.send_message(
                conversation_id=conversation_id,
                content=data.content,
                model_override=data.model,
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except ConversationNotFoundError as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.patch(
    "/{conversation_id}/messages/{message_id}",
    response_model=MessageResponse,
    summary="Edit a message",
)
async def edit_message(
    conversation_id: UUID,
    message_id: UUID,
    data: MessageUpdate,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
    auth: dict = Depends(require_any_role),
) -> MessageResponse:
    """Edit an existing message's content."""
    try:
        user_id, is_admin = _extract_user_context(auth)
        # Verify conversation ownership
        await service.get_conversation(
            conversation_id, user_id=user_id, is_admin=is_admin
        )

        # Update the message
        message = await service.update_message(message_id, data.content)
        return message_to_response(message)
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{conversation_id}/export",
    response_model=ConversationExport,
    summary="Export conversation",
)
async def export_conversation(
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
    auth: dict = Depends(require_any_role),
) -> ConversationExport:
    """Export a conversation with all messages in a portable format."""
    try:
        user_id, is_admin = _extract_user_context(auth)
        # Verify ownership first
        await service.get_conversation(
            conversation_id, user_id=user_id, is_admin=is_admin
        )
        return await service.export_conversation(conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
