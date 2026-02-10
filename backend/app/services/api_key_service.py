"""API key service for multi-provider AI API key management."""

import asyncio
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.encryption import decrypt_value, encrypt_value
from app.models.api_key import APIKey, APIKeyProvider, APIKeyStatus


class APIKeyService:
    """Service class for managing AI provider API keys."""

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db
        settings = get_settings()
        self.secret_key = settings.secret_key

    async def list_keys(self, provider: Optional[APIKeyProvider] = None) -> list[APIKey]:
        """List all API keys, optionally filtered by provider.

        Args:
            provider: Optional provider filter.

        Returns:
            List of APIKey objects.
        """
        query = select(APIKey).order_by(APIKey.created_at.desc())

        if provider:
            query = query.where(APIKey.provider == provider)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_key(self, key_id: UUID) -> Optional[APIKey]:
        """Get an API key by ID.

        Args:
            key_id: API key UUID.

        Returns:
            APIKey object or None if not found.
        """
        result = await self.db.execute(
            select(APIKey).where(APIKey.id == key_id)
        )
        return result.scalar_one_or_none()

    async def create_key(
        self,
        provider: APIKeyProvider,
        name: str,
        api_key: str,
        is_default: bool = False,
    ) -> APIKey:
        """Create a new API key.

        Args:
            provider: AI provider type.
            name: Display name for the key.
            api_key: Plain text API key (will be encrypted).
            is_default: Whether this is the default key for this provider.

        Returns:
            Created APIKey object.
        """
        # If setting as default, unset other defaults for this provider
        if is_default:
            await self._unset_defaults(provider)

        encrypted_key = encrypt_value(api_key, self.secret_key)

        key = APIKey(
            provider=provider,
            name=name,
            encrypted_key=encrypted_key,
            is_default=is_default,
            is_active=True,
            test_status=APIKeyStatus.UNTESTED,
        )

        self.db.add(key)
        await self.db.flush()
        await self.db.refresh(key)
        return key

    async def update_key(
        self,
        key_id: UUID,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[APIKey]:
        """Update an API key.

        Args:
            key_id: API key UUID.
            name: New name (optional).
            is_active: New active status (optional).

        Returns:
            Updated APIKey object or None if not found.
        """
        key = await self.get_key(key_id)
        if not key:
            return None

        if name is not None:
            key.name = name

        if is_active is not None:
            key.is_active = is_active

        await self.db.flush()
        await self.db.refresh(key)
        return key

    async def delete_key(self, key_id: UUID) -> bool:
        """Delete an API key.

        Args:
            key_id: API key UUID.

        Returns:
            True if deleted, False if not found.
        """
        key = await self.get_key(key_id)
        if not key:
            return False

        await self.db.delete(key)
        await self.db.flush()
        return True

    async def set_default(self, key_id: UUID) -> Optional[APIKey]:
        """Set an API key as the default for its provider.

        Args:
            key_id: API key UUID.

        Returns:
            Updated APIKey object or None if not found.
        """
        key = await self.get_key(key_id)
        if not key:
            return None

        # Unset other defaults for this provider
        await self._unset_defaults(key.provider)

        key.is_default = True
        await self.db.flush()
        await self.db.refresh(key)
        return key

    async def rotate_key(self, key_id: UUID, new_api_key: str) -> Optional[APIKey]:
        """Rotate an API key by replacing its value.

        Args:
            key_id: API key UUID.
            new_api_key: New plain text API key.

        Returns:
            Updated APIKey object or None if not found.
        """
        key = await self.get_key(key_id)
        if not key:
            return None

        # Create a new key with reference to old
        new_key = APIKey(
            provider=key.provider,
            name=key.name,
            encrypted_key=encrypt_value(new_api_key, self.secret_key),
            is_default=key.is_default,
            is_active=True,
            test_status=APIKeyStatus.UNTESTED,
            rotated_from_id=key.id,
        )

        # Deactivate old key
        key.is_active = False
        key.is_default = False

        self.db.add(new_key)
        await self.db.flush()
        await self.db.refresh(new_key)
        return new_key

    async def test_key(self, key_id: UUID) -> dict:
        """Test an API key's connectivity.

        Args:
            key_id: API key UUID.

        Returns:
            Dict with 'valid', 'error', and 'latency_ms' fields.
        """
        key = await self.get_key(key_id)
        if not key:
            return {"valid": False, "error": "Key not found", "latency_ms": None}

        # Decrypt the key
        api_key = decrypt_value(key.encrypted_key, self.secret_key)

        # Test based on provider
        start_time = datetime.now(timezone.utc)

        try:
            if key.provider == APIKeyProvider.OPENROUTER:
                valid, error = await self._test_openrouter(api_key)
            elif key.provider == APIKeyProvider.OPENAI:
                valid, error = await self._test_openai(api_key)
            elif key.provider == APIKeyProvider.ANTHROPIC:
                valid, error = await self._test_anthropic(api_key)
            elif key.provider == APIKeyProvider.GOOGLE:
                valid, error = await self._test_google(api_key)
            else:
                # For custom/unknown providers, just mark as untested
                return {"valid": None, "error": "Cannot test custom provider", "latency_ms": None}

            latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

            # Update key status
            key.last_tested_at = datetime.now(timezone.utc)
            key.test_status = APIKeyStatus.VALID if valid else APIKeyStatus.INVALID
            key.test_error = error if not valid else None
            await self.db.flush()

            return {"valid": valid, "error": error, "latency_ms": latency_ms}

        except Exception as e:
            key.last_tested_at = datetime.now(timezone.utc)
            key.test_status = APIKeyStatus.INVALID
            key.test_error = str(e)
            await self.db.flush()
            return {"valid": False, "error": str(e), "latency_ms": None}

    async def get_active_key(self, provider: APIKeyProvider) -> Optional[str]:
        """Get the decrypted active/default key for a provider.

        Args:
            provider: AI provider type.

        Returns:
            Decrypted API key string or None if no active key.
        """
        # First try to get default key
        result = await self.db.execute(
            select(APIKey)
            .where(APIKey.provider == provider)
            .where(APIKey.is_active == True)  # noqa: E712
            .where(APIKey.is_default == True)  # noqa: E712
        )
        key = result.scalar_one_or_none()

        # If no default, get any active key
        if not key:
            result = await self.db.execute(
                select(APIKey)
                .where(APIKey.provider == provider)
                .where(APIKey.is_active == True)  # noqa: E712
                .order_by(APIKey.created_at.desc())
                .limit(1)
            )
            key = result.scalar_one_or_none()

        if not key:
            return None

        # Update last used
        key.last_used_at = datetime.now(timezone.utc)
        await self.db.flush()

        return decrypt_value(key.encrypted_key, self.secret_key)

    def mask_key(self, api_key: str) -> str:
        """Mask an API key for display.

        Shows first 4 and last 4 characters.

        Args:
            api_key: Plain text API key.

        Returns:
            Masked key string.
        """
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return f"{api_key[:4]}...{api_key[-4:]}"

    async def _unset_defaults(self, provider: APIKeyProvider) -> None:
        """Unset default flag for all keys of a provider."""
        result = await self.db.execute(
            select(APIKey)
            .where(APIKey.provider == provider)
            .where(APIKey.is_default == True)  # noqa: E712
        )
        keys = result.scalars().all()
        for key in keys:
            key.is_default = False
        await self.db.flush()

    async def _test_openrouter(self, api_key: str) -> tuple[bool, Optional[str]]:
        """Test OpenRouter API key."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://openrouter.ai/api/v1/auth/key",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return True, None
                else:
                    return False, f"HTTP {response.status_code}: {response.text[:200]}"
            except httpx.TimeoutException:
                return False, "Connection timeout"
            except Exception as e:
                return False, str(e)

    async def _test_openai(self, api_key: str) -> tuple[bool, Optional[str]]:
        """Test OpenAI API key."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return True, None
                else:
                    return False, f"HTTP {response.status_code}: {response.text[:200]}"
            except httpx.TimeoutException:
                return False, "Connection timeout"
            except Exception as e:
                return False, str(e)

    async def _test_anthropic(self, api_key: str) -> tuple[bool, Optional[str]]:
        """Test Anthropic API key."""
        async with httpx.AsyncClient() as client:
            try:
                # Anthropic doesn't have a simple auth check endpoint,
                # so we make a minimal request
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "Hi"}],
                    },
                    timeout=10.0,
                )
                # Any response other than 401 means the key is valid
                if response.status_code in (200, 400, 429):
                    return True, None
                elif response.status_code == 401:
                    return False, "Invalid API key"
                else:
                    return False, f"HTTP {response.status_code}: {response.text[:200]}"
            except httpx.TimeoutException:
                return False, "Connection timeout"
            except Exception as e:
                return False, str(e)

    async def _test_google(self, api_key: str) -> tuple[bool, Optional[str]]:
        """Test Google AI API key."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return True, None
                else:
                    return False, f"HTTP {response.status_code}: {response.text[:200]}"
            except httpx.TimeoutException:
                return False, "Connection timeout"
            except Exception as e:
                return False, str(e)
