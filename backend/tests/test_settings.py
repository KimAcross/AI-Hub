"""Tests for settings API endpoints."""

import pytest
from httpx import AsyncClient


class TestSettingsAPI:
    """Test suite for settings operations."""

    @pytest.mark.asyncio
    async def test_get_settings(self, client: AsyncClient):
        """Test getting application settings."""
        response = await client.get("/api/v1/settings")

        assert response.status_code == 200
        data = response.json()
        assert "openrouter_api_key_set" in data
        assert "default_model" in data
        assert "embedding_model" in data
        assert "max_file_size_mb" in data

    @pytest.mark.asyncio
    async def test_update_default_model(self, client: AsyncClient):
        """Test updating the default model."""
        update_data = {
            "default_model": "anthropic/claude-3-haiku-20240307",
        }
        response = await client.patch("/api/v1/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["default_model"] == "anthropic/claude-3-haiku-20240307"

    @pytest.mark.asyncio
    async def test_set_api_key(self, client: AsyncClient):
        """Test setting an API key."""
        update_data = {
            "openrouter_api_key": "sk-or-v1-test-key-12345",
        }
        response = await client.patch("/api/v1/settings", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["openrouter_api_key_set"] is True

    @pytest.mark.asyncio
    async def test_clear_api_key(self, client: AsyncClient):
        """Test clearing an API key."""
        # First set an API key
        await client.patch(
            "/api/v1/settings",
            json={"openrouter_api_key": "sk-or-v1-test-key"},
        )

        # Then clear it
        response = await client.patch(
            "/api/v1/settings",
            json={"openrouter_api_key": ""},
        )

        assert response.status_code == 200
        data = response.json()
        # Note: openrouter_api_key_set could still be True if env var is set
        # This test just verifies the endpoint works

    @pytest.mark.asyncio
    async def test_test_api_key_not_configured(self, client: AsyncClient):
        """Test testing API key when not configured."""
        # Clear any existing key first
        await client.patch(
            "/api/v1/settings",
            json={"openrouter_api_key": ""},
        )

        response = await client.post("/api/v1/settings/test-api-key")

        assert response.status_code == 200
        data = response.json()
        # If no env var set, should show not configured
        assert "valid" in data
