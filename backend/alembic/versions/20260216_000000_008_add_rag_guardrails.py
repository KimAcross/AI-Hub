"""Add per-assistant RAG guardrail fields.

Revision ID: 008
Revises: 007
Create Date: 2026-02-16 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistants",
        sa.Column("max_retrieval_chunks", sa.Integer(), nullable=False, server_default="5"),
    )
    op.add_column(
        "assistants",
        sa.Column("max_context_tokens", sa.Integer(), nullable=False, server_default="4000"),
    )


def downgrade() -> None:
    op.drop_column("assistants", "max_context_tokens")
    op.drop_column("assistants", "max_retrieval_chunks")
