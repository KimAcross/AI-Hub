"""Settings service for managing application configuration."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.encryption import decrypt_if_needed, encrypt_value
from app.models.settings import Settings


class SettingsService:
    """Service for managing application settings stored in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, key: str, default: str | None = None) -> str | None:
        """Get a setting value by key."""
        result = await self.db.execute(select(Settings).where(Settings.key == key))
        setting = result.scalar_one_or_none()
        return setting.value if setting else default

    async def set(self, key: str, value: str) -> None:
        """Set a setting value."""
        result = await self.db.execute(select(Settings).where(Settings.key == key))
        setting = result.scalar_one_or_none()

        if setting:
            setting.value = value
        else:
            setting = Settings(key=key, value=value)
            self.db.add(setting)

        await self.db.commit()

    async def delete(self, key: str) -> bool:
        """Delete a setting by key."""
        result = await self.db.execute(select(Settings).where(Settings.key == key))
        setting = result.scalar_one_or_none()

        if setting:
            await self.db.delete(setting)
            await self.db.commit()
            return True
        return False

    async def get_openrouter_api_key(self) -> str | None:
        """Get the OpenRouter API key (decrypted).

        The API key is stored encrypted at rest and decrypted on retrieval.
        """
        encrypted_key = await self.get("openrouter_api_key")
        if not encrypted_key:
            return None

        settings = get_settings()
        return decrypt_if_needed(encrypted_key, settings.secret_key)

    async def set_openrouter_api_key(self, key: str | None) -> None:
        """Set or clear the OpenRouter API key.

        The API key is encrypted before storage.
        """
        if key:
            settings = get_settings()
            # Always encrypt before storing
            encrypted_key = encrypt_value(key, settings.secret_key)
            await self.set("openrouter_api_key", encrypted_key)
        else:
            await self.delete("openrouter_api_key")

    async def get_default_model(self) -> str:
        """Get the default model."""
        return (
            await self.get("default_model", "anthropic/claude-3.5-sonnet")
            or "anthropic/claude-3.5-sonnet"
        )

    async def set_default_model(self, model: str) -> None:
        """Set the default model."""
        await self.set("default_model", model)

    async def get_language(self) -> str:
        """Get the preferred language."""
        return await self.get("language", "en") or "en"

    async def set_language(self, language: str) -> None:
        """Set the preferred language."""
        await self.set("language", language)

    async def get_streaming_enabled(self) -> bool:
        """Get whether streaming is enabled."""
        value = await self.get("streaming_enabled", "true")
        return value.lower() == "true" if value else True

    async def set_streaming_enabled(self, enabled: bool) -> None:
        """Set whether streaming is enabled."""
        await self.set("streaming_enabled", "true" if enabled else "false")

    async def get_auto_save_interval(self) -> int:
        """Get the auto-save interval in seconds."""
        value = await self.get("auto_save_interval", "30")
        try:
            return int(value) if value else 30
        except ValueError:
            return 30

    async def set_auto_save_interval(self, interval: int) -> None:
        """Set the auto-save interval in seconds."""
        await self.set("auto_save_interval", str(interval))
