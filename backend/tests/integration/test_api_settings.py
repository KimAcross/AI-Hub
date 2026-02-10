"""Integration tests for the settings API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSettingsAPI:
    """Integration tests for /api/v1/settings endpoints."""

    async def test_get_settings(self, client: AsyncClient):
        """Test getting application settings."""
        response = await client.get("/api/v1/settings")
        assert response.status_code == 200

        data = response.json()
        assert "openrouter_api_key_set" in data
        assert "default_model" in data
        assert "embedding_model" in data
        assert "max_file_size_mb" in data
        assert "language" in data
        assert "streaming_enabled" in data
        assert "auto_save_interval" in data

    async def test_update_default_model(self, client: AsyncClient):
        """Test updating the default model setting."""
        new_model = "openai/gpt-4-turbo"

        response = await client.patch(
            "/api/v1/settings", json={"default_model": new_model}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["default_model"] == new_model

    async def test_update_language(self, client: AsyncClient):
        """Test updating the language setting."""
        new_language = "es"

        response = await client.patch(
            "/api/v1/settings", json={"language": new_language}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["language"] == new_language

    async def test_update_streaming_enabled(self, client: AsyncClient):
        """Test toggling streaming setting."""
        # Disable streaming
        response = await client.patch(
            "/api/v1/settings", json={"streaming_enabled": False}
        )
        assert response.status_code == 200
        assert response.json()["streaming_enabled"] is False

        # Re-enable streaming
        response = await client.patch(
            "/api/v1/settings", json={"streaming_enabled": True}
        )
        assert response.status_code == 200
        assert response.json()["streaming_enabled"] is True

    async def test_update_auto_save_interval(self, client: AsyncClient):
        """Test updating auto-save interval."""
        new_interval = 60

        response = await client.patch(
            "/api/v1/settings", json={"auto_save_interval": new_interval}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["auto_save_interval"] == new_interval

    async def test_update_auto_save_interval_disable(self, client: AsyncClient):
        """Test disabling auto-save (interval = 0)."""
        response = await client.patch(
            "/api/v1/settings", json={"auto_save_interval": 0}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["auto_save_interval"] == 0

    async def test_update_auto_save_interval_validation(self, client: AsyncClient):
        """Test auto-save interval validation (max 300)."""
        # Should reject values over 300
        response = await client.patch(
            "/api/v1/settings", json={"auto_save_interval": 500}
        )
        assert response.status_code == 422

    async def test_update_multiple_settings(self, client: AsyncClient):
        """Test updating multiple settings at once."""
        updates = {
            "default_model": "anthropic/claude-3-opus",
            "language": "fr",
            "streaming_enabled": False,
            "auto_save_interval": 120,
        }

        response = await client.patch("/api/v1/settings", json=updates)
        assert response.status_code == 200

        data = response.json()
        assert data["default_model"] == updates["default_model"]
        assert data["language"] == updates["language"]
        assert data["streaming_enabled"] == updates["streaming_enabled"]
        assert data["auto_save_interval"] == updates["auto_save_interval"]


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Integration tests for health check endpoints."""

    async def test_health_check(self, client: AsyncClient):
        """Test basic health check endpoint."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

    async def test_readiness_check(self, client: AsyncClient):
        """Test readiness check endpoint."""
        response = await client.get("/api/v1/ready")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "database" in data
