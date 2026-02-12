"""Assistant service for CRUD operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AssistantNotFoundError
from app.models.assistant import Assistant
from app.models.knowledge_file import KnowledgeFile
from app.schemas.assistant import (
    AssistantCreate,
    AssistantResponse,
    AssistantTemplate,
    AssistantUpdate,
    get_assistant_templates,
    get_template_by_id,
)


class AssistantService:
    """Service class for assistant CRUD operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db

    async def create_assistant(self, data: AssistantCreate) -> Assistant:
        """Create a new assistant."""
        assistant = Assistant(
            name=data.name,
            description=data.description,
            instructions=data.instructions,
            model=data.model,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
            avatar_url=data.avatar_url,
        )
        self.db.add(assistant)
        await self.db.flush()
        await self.db.refresh(assistant, ["knowledge_files"])
        return assistant

    async def create_from_template(self, template_id: str) -> Assistant:
        """Create an assistant from a template."""
        template = get_template_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        create_data = AssistantCreate(
            name=template.name,
            description=template.description,
            instructions=template.instructions,
            model=template.model,
            temperature=template.temperature,
            max_tokens=template.max_tokens,
        )
        return await self.create_assistant(create_data)

    async def get_assistant(self, assistant_id: UUID) -> Assistant:
        """Get an assistant by ID."""
        result = await self.db.execute(
            select(Assistant)
            .options(selectinload(Assistant.knowledge_files))
            .where(Assistant.id == assistant_id)
            .where(Assistant.is_deleted == False)  # noqa: E712
        )
        assistant = result.scalar_one_or_none()
        if not assistant:
            raise AssistantNotFoundError(str(assistant_id))
        return assistant

    async def list_assistants(
        self,
        include_deleted: bool = False,
    ) -> tuple[list[Assistant], int]:
        """List all assistants with file counts."""
        query = select(Assistant).options(selectinload(Assistant.knowledge_files))

        if not include_deleted:
            query = query.where(Assistant.is_deleted == False)  # noqa: E712

        query = query.order_by(Assistant.created_at.desc())

        result = await self.db.execute(query)
        assistants = result.scalars().all()

        return list(assistants), len(assistants)

    async def update_assistant(
        self,
        assistant_id: UUID,
        data: AssistantUpdate,
    ) -> Assistant:
        """Update an existing assistant."""
        assistant = await self.get_assistant(assistant_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assistant, field, value)

        await self.db.flush()
        await self.db.refresh(assistant, ["knowledge_files"])
        return assistant

    async def delete_assistant(self, assistant_id: UUID) -> None:
        """Soft delete an assistant."""
        assistant = await self.get_assistant(assistant_id)
        assistant.is_deleted = True
        await self.db.flush()

    async def restore_assistant(self, assistant_id: UUID) -> Assistant:
        """Restore a soft-deleted assistant."""
        result = await self.db.execute(
            select(Assistant)
            .where(Assistant.id == assistant_id)
            .where(Assistant.is_deleted == True)  # noqa: E712
        )
        assistant = result.scalar_one_or_none()
        if not assistant:
            raise AssistantNotFoundError(str(assistant_id))

        assistant.is_deleted = False
        await self.db.flush()
        await self.db.refresh(assistant, ["knowledge_files"])
        return assistant

    async def get_file_count(self, assistant_id: UUID) -> int:
        """Get the number of files for an assistant."""
        result = await self.db.execute(
            select(func.count())
            .select_from(KnowledgeFile)
            .where(KnowledgeFile.assistant_id == assistant_id)
            .where(KnowledgeFile.status == "ready")
        )
        return result.scalar() or 0

    def get_templates(self) -> list[AssistantTemplate]:
        """Get all available assistant templates."""
        return get_assistant_templates()

    def get_template(self, template_id: str) -> Optional[AssistantTemplate]:
        """Get a specific template by ID."""
        return get_template_by_id(template_id)


def assistant_to_response(assistant: Assistant) -> AssistantResponse:
    """Convert an Assistant model to response schema."""
    file_count = len([f for f in assistant.knowledge_files if f.status == "ready"])
    return AssistantResponse(
        id=assistant.id,
        name=assistant.name,
        description=assistant.description,
        instructions=assistant.instructions,
        model=assistant.model,
        temperature=assistant.temperature,
        max_tokens=assistant.max_tokens,
        avatar_url=assistant.avatar_url,
        file_count=file_count,
        is_deleted=assistant.is_deleted,
        created_at=assistant.created_at,
        updated_at=assistant.updated_at,
    )
