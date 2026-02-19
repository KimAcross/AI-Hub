"""Application configuration using Pydantic Settings."""

import logging
from functools import lru_cache
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AI-Across"
    app_env: str = "development"
    debug: bool = False  # Secure default: disabled
    log_level: str = "INFO"
    log_format: str = "json"

    # Database
    database_url: str = "postgresql+asyncpg://aiacross:aiacross@localhost:5432/aiacross"

    # OpenRouter
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-3.5-sonnet"

    # Embeddings
    embedding_model: str = "text-embedding-3-small"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"

    # File Storage
    upload_dir: str = "./data/uploads"
    max_file_size_mb: int = 50
    ingestion_reaper_interval_seconds: int = 300
    ingestion_stale_processing_minutes: int = 15

    # Security
    secret_key: str = "change-this-secret-key-in-production"
    access_token_expire_hours: int = 8

    # Admin - supports both plaintext (dev) and bcrypt hash (prod)
    admin_password: Optional[str] = None

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_login: str = "5/minute"
    rate_limit_chat: str = "30/minute"
    rate_limit_upload: str = "10/minute"
    rate_limit_settings: str = "10/minute"

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == "production"

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate critical settings for production deployment."""
        if self.is_production:
            # Fail fast if SECRET_KEY is default in production
            if self.secret_key == "change-this-secret-key-in-production":
                raise ValueError(
                    "SECRET_KEY must be changed from default value in production. "
                    'Generate a secure key with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
                )

            # Warn if DEBUG is enabled in production
            if self.debug:
                logger.warning(
                    "DEBUG is enabled in production. This exposes sensitive information. "
                    "Set DEBUG=false for production deployments."
                )

            # Warn if admin password is not set
            if not self.admin_password:
                logger.warning(
                    "ADMIN_PASSWORD is not set. Admin dashboard will be inaccessible."
                )
            elif not self.admin_password.startswith("$2"):
                # Warn if admin password is not bcrypt hashed
                logger.warning(
                    "ADMIN_PASSWORD appears to be plaintext. For production, use a bcrypt hash. "
                    "Generate with: python -c \"import bcrypt; print(bcrypt.hashpw(b'your-password', bcrypt.gensalt()).decode())\""
                )

            # Validate CORS origins don't contain wildcards
            for origin in self.cors_origins:
                if "*" in origin:
                    raise ValueError(
                        f"CORS wildcard origins not allowed in production: {origin}. "
                        "Specify explicit allowed origins."
                    )

        return self


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
