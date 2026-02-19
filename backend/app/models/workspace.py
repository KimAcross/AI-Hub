"""Workspace database model for future client isolation."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.assistant import Assistant
    from app.models.conversation import Conversation
    from app.models.knowledge_file import KnowledgeFile


class Workspace(Base):
    """Workspace container model."""

    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    assistants: Mapped[List["Assistant"]] = relationship("Assistant")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation")
    knowledge_files: Mapped[List["KnowledgeFile"]] = relationship("KnowledgeFile")
