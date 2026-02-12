"""Add workspace_id to core tables for future client isolation.

Revision ID: 007
Revises: 006
Create Date: 2026-02-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Fixed UUID for the default workspace (deterministic for backfilling)
DEFAULT_WORKSPACE_ID = "00000000-0000-4000-8000-000000000001"


def upgrade() -> None:
    # 1. Create workspaces table
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 2. Insert default workspace
    op.execute(
        f"INSERT INTO workspaces (id, name, slug) "
        f"VALUES ('{DEFAULT_WORKSPACE_ID}', 'Default', 'default')"
    )

    # 3. Add workspace_id to assistants
    op.add_column(
        "assistants",
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
    op.execute(f"UPDATE assistants SET workspace_id = '{DEFAULT_WORKSPACE_ID}'")
    op.create_index("ix_assistants_workspace_id", "assistants", ["workspace_id"])

    # 4. Add workspace_id to conversations
    op.add_column(
        "conversations",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_conversations_workspace_id",
        "conversations",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(f"UPDATE conversations SET workspace_id = '{DEFAULT_WORKSPACE_ID}'")
    op.create_index("ix_conversations_workspace_id", "conversations", ["workspace_id"])

    # 5. Add workspace_id to knowledge_files
    op.add_column(
        "knowledge_files",
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_knowledge_files_workspace_id",
        "knowledge_files",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(f"UPDATE knowledge_files SET workspace_id = '{DEFAULT_WORKSPACE_ID}'")
    op.create_index("ix_knowledge_files_workspace_id", "knowledge_files", ["workspace_id"])


def downgrade() -> None:
    # knowledge_files
    op.drop_index("ix_knowledge_files_workspace_id", table_name="knowledge_files")
    op.drop_constraint("fk_knowledge_files_workspace_id", "knowledge_files", type_="foreignkey")
    op.drop_column("knowledge_files", "workspace_id")

    # conversations
    op.drop_index("ix_conversations_workspace_id", table_name="conversations")
    op.drop_constraint("fk_conversations_workspace_id", "conversations", type_="foreignkey")
    op.drop_column("conversations", "workspace_id")

    # assistants
    op.drop_index("ix_assistants_workspace_id", table_name="assistants")
    op.drop_constraint("fk_assistants_workspace_id", "assistants", type_="foreignkey")
    op.drop_column("assistants", "workspace_id")

    # workspaces table
    op.drop_table("workspaces")
