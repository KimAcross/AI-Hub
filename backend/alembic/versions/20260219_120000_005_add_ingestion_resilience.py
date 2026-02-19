"""Add ingestion resilience columns to knowledge_files.

Revision ID: 005
Revises: 004
Create Date: 2026-02-19 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "knowledge_files",
        sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "knowledge_files",
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "knowledge_files",
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
    )
    op.add_column(
        "knowledge_files",
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("knowledge_files", sa.Column("last_error", sa.Text(), nullable=True))
    op.create_index(
        "ix_knowledge_files_next_retry_at",
        "knowledge_files",
        ["next_retry_at"],
        unique=False,
    )
    op.execute(
        "UPDATE knowledge_files SET attempt_count = 0, max_attempts = 3 WHERE attempt_count IS NULL OR max_attempts IS NULL"
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_files_next_retry_at", table_name="knowledge_files")
    op.drop_column("knowledge_files", "last_error")
    op.drop_column("knowledge_files", "next_retry_at")
    op.drop_column("knowledge_files", "max_attempts")
    op.drop_column("knowledge_files", "attempt_count")
    op.drop_column("knowledge_files", "processing_started_at")
