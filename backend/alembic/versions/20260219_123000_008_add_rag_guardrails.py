"""Add per-assistant RAG guardrail settings.

Revision ID: 008
Revises: 007
Create Date: 2026-02-19 12:30:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistants",
        sa.Column(
            "max_retrieval_chunks", sa.Integer(), nullable=False, server_default="5"
        ),
    )
    op.add_column(
        "assistants",
        sa.Column(
            "max_context_tokens", sa.Integer(), nullable=False, server_default="4000"
        ),
    )
    op.execute(
        "UPDATE assistants SET max_retrieval_chunks = 5, max_context_tokens = 4000 "
        "WHERE max_retrieval_chunks IS NULL OR max_context_tokens IS NULL"
    )


def downgrade() -> None:
    op.drop_column("assistants", "max_context_tokens")
    op.drop_column("assistants", "max_retrieval_chunks")
