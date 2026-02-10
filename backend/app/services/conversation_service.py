"""Conversation service for CRUD operations and chat functionality."""

import uuid
from typing import Any, AsyncIterator, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    AssistantNotFoundError,
    ConversationNotFoundError,
    QuotaExceededError,
)
from app.models.assistant import Assistant
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationExport,
    ConversationResponse,
    ConversationUpdate,
    MessageResponse,
)
from app.services.openrouter_service import OpenRouterService, get_openrouter_service
from app.services.rag_service import RAGService, get_rag_service


class ConversationService:
    """Service class for conversation CRUD operations."""

    def __init__(
        self,
        db: AsyncSession,
        openrouter_service: Optional[OpenRouterService] = None,
        rag_service: Optional[RAGService] = None,
    ):
        """Initialize the service with a database session."""
        self.db = db
        self.openrouter = openrouter_service or get_openrouter_service()
        self.rag = rag_service or get_rag_service()

    async def create_conversation(
        self, data: ConversationCreate, user_id: Optional[uuid.UUID] = None
    ) -> Conversation:
        """Create a new conversation.

        Args:
            data: Conversation creation data.
            user_id: UUID of the owning user.

        Returns:
            Created conversation.

        Raises:
            AssistantNotFoundError: If assistant doesn't exist.
        """
        # Verify assistant exists
        result = await self.db.execute(
            select(Assistant)
            .where(Assistant.id == data.assistant_id)
            .where(Assistant.is_deleted == False)  # noqa: E712
        )
        assistant = result.scalar_one_or_none()
        if not assistant:
            raise AssistantNotFoundError(str(data.assistant_id))

        conversation = Conversation(
            assistant_id=data.assistant_id,
            title=data.title,
            user_id=user_id,
        )
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        is_admin: bool = False,
    ) -> Conversation:
        """Get a conversation by ID with messages.

        Args:
            conversation_id: UUID of the conversation.
            user_id: UUID of the requesting user (for ownership check).
            is_admin: Whether the requesting user is an admin.

        Returns:
            Conversation with messages loaded.

        Raises:
            ConversationNotFoundError: If conversation doesn't exist or user doesn't own it.
        """
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .options(selectinload(Conversation.assistant))
            .where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise ConversationNotFoundError(str(conversation_id))

        # Ownership check: non-admin users can only access their own conversations
        if user_id and not is_admin and conversation.user_id != user_id:
            raise ConversationNotFoundError(str(conversation_id))

        return conversation

    async def list_conversations(
        self,
        assistant_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        is_admin: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Conversation], int]:
        """List conversations with optional filtering.

        Args:
            assistant_id: Filter by assistant ID.
            user_id: Filter by user ID (for user isolation).
            is_admin: Whether the requesting user is an admin.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            Tuple of (conversations list, total count).
        """
        query = select(Conversation).options(selectinload(Conversation.messages))

        if assistant_id:
            query = query.where(Conversation.assistant_id == assistant_id)

        # User isolation: non-admin users only see their own conversations
        if user_id and not is_admin:
            query = query.where(Conversation.user_id == user_id)

        query = query.order_by(Conversation.updated_at.desc())

        # Get total count
        count_query = select(func.count()).select_from(Conversation)
        if assistant_id:
            count_query = count_query.where(Conversation.assistant_id == assistant_id)
        if user_id and not is_admin:
            count_query = count_query.where(Conversation.user_id == user_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        conversations = result.scalars().all()

        return list(conversations), total

    async def update_conversation(
        self,
        conversation_id: uuid.UUID,
        data: ConversationUpdate,
    ) -> Conversation:
        """Update a conversation.

        Args:
            conversation_id: UUID of the conversation.
            data: Update data.

        Returns:
            Updated conversation.
        """
        conversation = await self.get_conversation(conversation_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conversation, field, value)

        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def delete_conversation(self, conversation_id: uuid.UUID) -> None:
        """Delete a conversation and all its messages.

        Args:
            conversation_id: UUID of the conversation.
        """
        conversation = await self.get_conversation(conversation_id)
        await self.db.delete(conversation)
        await self.db.flush()

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        model: Optional[str] = None,
        tokens_used: Optional[dict[str, Any]] = None,
    ) -> Message:
        """Add a message to a conversation.

        Args:
            conversation_id: UUID of the conversation.
            role: Message role ('user' or 'assistant').
            content: Message content.
            model: Model used (for assistant messages).
            tokens_used: Token usage information.

        Returns:
            Created message.
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            tokens_used=tokens_used,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def update_message(
        self,
        message_id: uuid.UUID,
        content: str,
    ) -> Message:
        """Update a message's content.

        Args:
            message_id: UUID of the message.
            content: New content.

        Returns:
            Updated message.

        Raises:
            ConversationNotFoundError: If message doesn't exist.
        """
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        if not message:
            raise ConversationNotFoundError(f"Message not found: {message_id}")

        message.content = content
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_message(self, message_id: uuid.UUID) -> Message:
        """Get a message by ID.

        Args:
            message_id: UUID of the message.

        Returns:
            Message object.
        """
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        if not message:
            raise ConversationNotFoundError(f"Message not found: {message_id}")
        return message

    async def send_message(
        self,
        conversation_id: uuid.UUID,
        content: str,
        model_override: Optional[str] = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Send a message and stream the assistant's response.

        Args:
            conversation_id: UUID of the conversation.
            content: User message content.
            model_override: Optional model to use instead of assistant default.

        Yields:
            Streaming response chunks.
        """
        # Get conversation with assistant
        conversation = await self.get_conversation(conversation_id)

        if not conversation.assistant:
            yield {"type": "error", "error": "Assistant not found for this conversation"}
            return

        assistant = conversation.assistant

        # Check quota before proceeding
        try:
            from app.services.quota_service import get_quota_service

            quota_service = get_quota_service(self.db)
            quota_result = await quota_service.check_quota()

            if not quota_result.allowed:
                yield {
                    "type": "error",
                    "error": f"Usage limit exceeded: {quota_result.reason}",
                    "quota_exceeded": True,
                }
                return
        except Exception as e:
            # Log but don't block if quota check fails
            import logging

            logging.getLogger(__name__).warning(f"Quota check failed: {e}")

        # Save user message
        user_message = await self.add_message(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

        yield {
            "type": "user_message",
            "message_id": str(user_message.id),
        }

        # Build message history for the API
        messages_for_api: list[dict[str, str]] = []

        # Get RAG-augmented system prompt
        try:
            system_prompt, retrieved_chunks = await self.rag.get_augmented_prompt(
                assistant_id=assistant.id,
                assistant_name=assistant.name,
                assistant_instructions=assistant.instructions,
                user_query=content,
            )
        except Exception:
            # Fallback to simple prompt if RAG fails
            system_prompt = f"You are {assistant.name}.\n\n{assistant.instructions}"
            retrieved_chunks = []

        messages_for_api.append({"role": "system", "content": system_prompt})

        # Add conversation history (exclude the message we just added)
        for msg in conversation.messages:
            if msg.id != user_message.id:
                messages_for_api.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        # Add the current user message
        messages_for_api.append({"role": "user", "content": content})

        # Determine which model to use
        model = model_override or assistant.model

        # Create placeholder for assistant message
        assistant_message = await self.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content="",
            model=model,
        )

        yield {
            "type": "assistant_message_start",
            "message_id": str(assistant_message.id),
        }

        # Stream the response
        full_content = ""
        tokens_used = None

        try:
            async for chunk in self.openrouter.stream_chat_completion(
                messages=messages_for_api,
                model=model,
                temperature=float(assistant.temperature),
                max_tokens=assistant.max_tokens,
            ):
                if chunk["type"] == "content":
                    full_content += chunk["content"]
                    yield {
                        "type": "content",
                        "content": chunk["content"],
                    }
                elif chunk["type"] == "done":
                    tokens_used = chunk.get("tokens_used")

                    # Log usage if we have token data
                    if tokens_used:
                        from app.services.usage_log_service import UsageLogService

                        usage_service = UsageLogService(self.db, self.openrouter)
                        await usage_service.log_usage(
                            assistant_id=assistant.id,
                            conversation_id=conversation_id,
                            message_id=assistant_message.id,
                            model=model,
                            prompt_tokens=tokens_used.get("prompt_tokens", 0),
                            completion_tokens=tokens_used.get("completion_tokens", 0),
                        )

                    yield {
                        "type": "done",
                        "message_id": str(assistant_message.id),
                        "tokens_used": tokens_used,
                    }
                elif chunk["type"] == "error":
                    yield chunk

            # Update assistant message with full content and tokens
            assistant_message.content = full_content
            if tokens_used:
                assistant_message.tokens_used = tokens_used

            await self.db.flush()

            # Auto-generate title from first message if needed
            if conversation.title == "New Conversation" and full_content:
                # Use first part of user message as title
                title = content[:50].strip()
                if len(content) > 50:
                    title += "..."
                conversation.title = title
                await self.db.flush()

        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
            }

    async def export_conversation(
        self,
        conversation_id: uuid.UUID,
    ) -> ConversationExport:
        """Export a conversation with all messages.

        Args:
            conversation_id: UUID of the conversation.

        Returns:
            Conversation export data.
        """
        conversation = await self.get_conversation(conversation_id)

        assistant_name = None
        if conversation.assistant:
            assistant_name = conversation.assistant.name

        messages = [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                model=msg.model,
                tokens_used=msg.tokens_used,
                created_at=msg.created_at,
            )
            for msg in conversation.messages
        ]

        return ConversationExport(
            id=conversation.id,
            title=conversation.title,
            assistant_name=assistant_name,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=messages,
        )


def conversation_to_response(conversation: Conversation) -> ConversationResponse:
    """Convert a Conversation model to response schema."""
    message_count = len(conversation.messages) if conversation.messages else 0
    return ConversationResponse(
        id=conversation.id,
        assistant_id=conversation.assistant_id,
        title=conversation.title,
        message_count=message_count,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


def message_to_response(message: Message) -> MessageResponse:
    """Convert a Message model to response schema."""
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        model=message.model,
        tokens_used=message.tokens_used,
        created_at=message.created_at,
    )
