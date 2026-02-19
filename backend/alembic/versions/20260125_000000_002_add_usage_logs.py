"""Add usage_logs table for tracking token usage and costs.

Revision ID: 002
Revises: 001
Create Date: 2026-01-25 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create usage_logs table
    op.create_table(
        "usage_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assistant_id", sa.UUID(), nullable=True),
        sa.Column("conversation_id", sa.UUID(), nullable=True),
        sa.Column(
            "message_id",
            sa.UUID(),
            nullable=True,
            comment="Reference to the assistant message that incurred this cost",
        ),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "completion_tokens", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "cost_usd",
            sa.Numeric(precision=10, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["assistant_id"],
            ["assistants.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for efficient aggregation queries
    op.create_index(
        "idx_usage_logs_created_at", "usage_logs", ["created_at"], unique=False
    )
    op.create_index(
        "idx_usage_logs_assistant_id", "usage_logs", ["assistant_id"], unique=False
    )
    op.create_index("idx_usage_logs_model", "usage_logs", ["model"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_usage_logs_model", table_name="usage_logs")
    op.drop_index("idx_usage_logs_assistant_id", table_name="usage_logs")
    op.drop_index("idx_usage_logs_created_at", table_name="usage_logs")
    op.drop_table("usage_logs")
