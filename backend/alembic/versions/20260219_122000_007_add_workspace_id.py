"""Add workspaces table and workspace_id columns.

Revision ID: 007
Revises: 006
Create Date: 2026-02-19 12:20:00.000000
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.add_column(
        "assistants",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "conversations",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "knowledge_files",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_foreign_key(
        "fk_assistants_workspace_id",
        "assistants",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_conversations_workspace_id",
        "conversations",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_knowledge_files_workspace_id",
        "knowledge_files",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index("ix_assistants_workspace_id", "assistants", ["workspace_id"])
    op.create_index("ix_conversations_workspace_id", "conversations", ["workspace_id"])
    op.create_index(
        "ix_knowledge_files_workspace_id", "knowledge_files", ["workspace_id"]
    )

    default_workspace_id = str(uuid.uuid4())
    op.execute(
        sa.text(
            "INSERT INTO workspaces (id, name, slug) VALUES (:id, :name, :slug)"
        ).bindparams(
            id=default_workspace_id,
            name="Default Workspace",
            slug="default",
        )
    )

    op.execute(
        sa.text(
            "UPDATE assistants SET workspace_id = :workspace_id WHERE workspace_id IS NULL"
        ).bindparams(workspace_id=default_workspace_id)
    )
    op.execute(
        sa.text(
            "UPDATE conversations SET workspace_id = :workspace_id WHERE workspace_id IS NULL"
        ).bindparams(workspace_id=default_workspace_id)
    )
    op.execute(
        sa.text(
            "UPDATE knowledge_files SET workspace_id = :workspace_id WHERE workspace_id IS NULL"
        ).bindparams(workspace_id=default_workspace_id)
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_files_workspace_id", table_name="knowledge_files")
    op.drop_index("ix_conversations_workspace_id", table_name="conversations")
    op.drop_index("ix_assistants_workspace_id", table_name="assistants")

    op.drop_constraint(
        "fk_knowledge_files_workspace_id", "knowledge_files", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_conversations_workspace_id", "conversations", type_="foreignkey"
    )
    op.drop_constraint("fk_assistants_workspace_id", "assistants", type_="foreignkey")

    op.drop_column("knowledge_files", "workspace_id")
    op.drop_column("conversations", "workspace_id")
    op.drop_column("assistants", "workspace_id")

    op.drop_table("workspaces")
