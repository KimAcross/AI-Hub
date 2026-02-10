"""Add admin features: users, api_keys, usage_quotas, audit_logs tables.

Revision ID: 003
Revises: 002
Create Date: 2026-02-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    user_role_enum = postgresql.ENUM("admin", "manager", "user", name="userrole", create_type=False)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    api_key_provider_enum = postgresql.ENUM(
        "openrouter", "openai", "anthropic", "google", "azure", "custom",
        name="apikeyprovider", create_type=False
    )
    api_key_provider_enum.create(op.get_bind(), checkfirst=True)

    api_key_status_enum = postgresql.ENUM("valid", "invalid", "untested", name="apikeystatus", create_type=False)
    api_key_status_enum.create(op.get_bind(), checkfirst=True)

    quota_scope_enum = postgresql.ENUM("global", "user", name="quotascope", create_type=False)
    quota_scope_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "manager", "user", name="userrole"),
            nullable=False,
            server_default="user",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("idx_users_email", "users", ["email"], unique=False)
    op.create_index("idx_users_role", "users", ["role"], unique=False)
    op.create_index("idx_users_is_active", "users", ["is_active"], unique=False)

    # Create user_api_keys table
    op.create_table(
        "user_api_keys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("key_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "key_prefix",
            sa.String(length=12),
            nullable=False,
            comment="First 8 characters for display identification",
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_user_api_keys_user_id", "user_api_keys", ["user_id"], unique=False)
    op.create_index("idx_user_api_keys_key_prefix", "user_api_keys", ["key_prefix"], unique=False)
    op.create_index("idx_user_api_keys_is_active", "user_api_keys", ["is_active"], unique=False)

    # Create api_keys table (for AI provider keys)
    op.create_table(
        "api_keys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "provider",
            sa.Enum("openrouter", "openai", "anthropic", "google", "azure", "custom", name="apikeyprovider"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "encrypted_key",
            sa.Text(),
            nullable=False,
            comment="Fernet-encrypted API key",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            comment="Default key for this provider",
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "test_status",
            sa.Enum("valid", "invalid", "untested", name="apikeystatus"),
            nullable=False,
            server_default="untested",
        ),
        sa.Column(
            "test_error",
            sa.String(length=500),
            nullable=True,
            comment="Error message from last test if failed",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "rotated_from_id",
            sa.UUID(),
            nullable=True,
            comment="Reference to previous key if this was rotated",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_api_keys_provider", "api_keys", ["provider"], unique=False)
    op.create_index("idx_api_keys_is_active", "api_keys", ["is_active"], unique=False)
    op.create_index("idx_api_keys_is_default", "api_keys", ["is_default"], unique=False)

    # Create usage_quotas table
    op.create_table(
        "usage_quotas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "scope",
            sa.Enum("global", "user", name="quotascope"),
            nullable=False,
            server_default="global",
        ),
        sa.Column(
            "scope_id",
            sa.String(length=100),
            nullable=True,
            comment="User ID if scope is USER, null for GLOBAL",
        ),
        sa.Column("daily_cost_limit_usd", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("monthly_cost_limit_usd", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("daily_token_limit", sa.Integer(), nullable=True),
        sa.Column("monthly_token_limit", sa.Integer(), nullable=True),
        sa.Column("requests_per_minute", sa.Integer(), nullable=True),
        sa.Column("requests_per_hour", sa.Integer(), nullable=True),
        sa.Column(
            "alert_threshold_percent",
            sa.Integer(),
            nullable=False,
            server_default="80",
            comment="Percentage at which to trigger alerts",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_usage_quotas_scope", "usage_quotas", ["scope"], unique=False)
    op.create_index("idx_usage_quotas_scope_id", "usage_quotas", ["scope_id"], unique=False)

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "action",
            sa.String(length=100),
            nullable=False,
            comment="Action performed: user.created, api_key.rotated, quota.updated, etc.",
        ),
        sa.Column(
            "resource_type",
            sa.String(length=50),
            nullable=False,
            comment="Type of resource: user, api_key, quota, settings",
        ),
        sa.Column(
            "resource_id",
            sa.String(length=100),
            nullable=True,
            comment="ID of the affected resource",
        ),
        sa.Column(
            "actor",
            sa.String(length=100),
            nullable=False,
            server_default="system",
            comment="User email or 'system' for automated actions",
        ),
        sa.Column(
            "actor_id",
            sa.String(length=100),
            nullable=True,
            comment="User ID of the actor if applicable",
        ),
        sa.Column(
            "ip_address",
            sa.String(length=45),
            nullable=True,
            comment="IPv4 or IPv6 address",
        ),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Additional context about the action",
        ),
        sa.Column(
            "old_values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Previous values before change",
        ),
        sa.Column(
            "new_values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="New values after change",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index("idx_audit_logs_resource_type", "audit_logs", ["resource_type"], unique=False)
    op.create_index("idx_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)
    op.create_index("idx_audit_logs_actor", "audit_logs", ["actor"], unique=False)
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)

    # Insert default global quota
    op.execute(
        """
        INSERT INTO usage_quotas (id, scope, alert_threshold_percent)
        VALUES (gen_random_uuid(), 'global', 80)
        """
    )


def downgrade() -> None:
    # Drop audit_logs
    op.drop_index("idx_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("idx_audit_logs_actor", table_name="audit_logs")
    op.drop_index("idx_audit_logs_resource_id", table_name="audit_logs")
    op.drop_index("idx_audit_logs_resource_type", table_name="audit_logs")
    op.drop_index("idx_audit_logs_action", table_name="audit_logs")
    op.drop_table("audit_logs")

    # Drop usage_quotas
    op.drop_index("idx_usage_quotas_scope_id", table_name="usage_quotas")
    op.drop_index("idx_usage_quotas_scope", table_name="usage_quotas")
    op.drop_table("usage_quotas")

    # Drop api_keys
    op.drop_index("idx_api_keys_is_default", table_name="api_keys")
    op.drop_index("idx_api_keys_is_active", table_name="api_keys")
    op.drop_index("idx_api_keys_provider", table_name="api_keys")
    op.drop_table("api_keys")

    # Drop user_api_keys
    op.drop_index("idx_user_api_keys_is_active", table_name="user_api_keys")
    op.drop_index("idx_user_api_keys_key_prefix", table_name="user_api_keys")
    op.drop_index("idx_user_api_keys_user_id", table_name="user_api_keys")
    op.drop_table("user_api_keys")

    # Drop users
    op.drop_index("idx_users_is_active", table_name="users")
    op.drop_index("idx_users_role", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS quotascope")
    op.execute("DROP TYPE IF EXISTS apikeystatus")
    op.execute("DROP TYPE IF EXISTS apikeyprovider")
    op.execute("DROP TYPE IF EXISTS userrole")
