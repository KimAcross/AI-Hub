"""Add user_id to conversations, cleanup pre-production data.

Revision ID: 004
Revises: 003
Create Date: 2026-02-10 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Delete all pre-production data
    op.execute("DELETE FROM messages")
    op.execute("DELETE FROM conversations")

    # 2. Add user_id column
    op.add_column(
        "conversations",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 3. Add foreign key
    op.create_foreign_key(
        "fk_conversations_user_id",
        "conversations",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 4. Add index for query performance
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_conversations_user_id", table_name="conversations")
    op.drop_constraint("fk_conversations_user_id", "conversations", type_="foreignkey")
    op.drop_column("conversations", "user_id")
