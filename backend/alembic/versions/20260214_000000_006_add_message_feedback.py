"""Add feedback columns to messages.

Revision ID: 006
Revises: 005
Create Date: 2026-02-14 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("feedback", sa.String(20), nullable=True),
    )
    op.add_column(
        "messages",
        sa.Column("feedback_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "messages",
        sa.Column("feedback_context", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_messages_feedback", "messages", ["feedback"])


def downgrade() -> None:
    op.drop_index("ix_messages_feedback", table_name="messages")
    op.drop_column("messages", "feedback_context")
    op.drop_column("messages", "feedback_reason")
    op.drop_column("messages", "feedback")
