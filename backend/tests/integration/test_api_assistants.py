"""Integration tests for the assistants API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAssistantsAPI:
    """Integration tests for /api/v1/assistants endpoints."""

    async def test_create_assistant(
        self, client: AsyncClient, sample_assistant_data: dict
    ):
        """Test creating a new assistant."""
        response = await client.post("/api/v1/assistants", json=sample_assistant_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == sample_assistant_data["name"]
        assert data["description"] == sample_assistant_data["description"]
        assert data["instructions"] == sample_assistant_data["instructions"]
        assert data["model"] == sample_assistant_data["model"]
        assert data["temperature"] == sample_assistant_data["temperature"]
        assert data["max_tokens"] == sample_assistant_data["max_tokens"]
        assert "id" in data
        assert data["is_deleted"] is False

    async def test_create_assistant_minimal(self, client: AsyncClient):
        """Test creating an assistant with insufficient required fields."""
        minimal_data = {
            "name": "Minimal Assistant",
            "instructions": "You are a minimal assistant.",
        }
        response = await client.post("/api/v1/assistants", json=minimal_data)
        assert response.status_code == 422

    async def test_create_assistant_validation_error(self, client: AsyncClient):
        """Test creating an assistant with invalid data."""
        invalid_data = {
            "name": "",  # Empty name should fail
            "instructions": "Test",
        }
        response = await client.post("/api/v1/assistants", json=invalid_data)
        assert response.status_code == 422

    async def test_list_assistants_empty(self, client: AsyncClient):
        """Test listing assistants when none exist."""
        response = await client.get("/api/v1/assistants")
        assert response.status_code == 200
        assert response.json()["assistants"] == []

    async def test_list_assistants(
        self, client: AsyncClient, sample_assistant_data: dict
    ):
        """Test listing assistants."""
        # Create an assistant first
        create_response = await client.post(
            "/api/v1/assistants", json=sample_assistant_data
        )
        assert create_response.status_code == 201

        # List assistants
        response = await client.get("/api/v1/assistants")
        assert response.status_code == 200

        data = response.json()
        assert len(data["assistants"]) == 1
        assert data["assistants"][0]["name"] == sample_assistant_data["name"]

    async def test_get_assistant(
        self, client: AsyncClient, sample_assistant_data: dict
    ):
        """Test getting a specific assistant by ID."""
        # Create an assistant first
        create_response = await client.post(
            "/api/v1/assistants", json=sample_assistant_data
        )
        assistant_id = create_response.json()["id"]

        # Get the assistant
        response = await client.get(f"/api/v1/assistants/{assistant_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == assistant_id
        assert data["name"] == sample_assistant_data["name"]

    async def test_get_assistant_not_found(self, client: AsyncClient):
        """Test getting a non-existent assistant."""
        response = await client.get("/api/v1/assistants/non-existent-id")
        assert response.status_code == 404

    async def test_update_assistant(
        self, client: AsyncClient, sample_assistant_data: dict
    ):
        """Test updating an assistant."""
        # Create an assistant first
        create_response = await client.post(
            "/api/v1/assistants", json=sample_assistant_data
        )
        assistant_id = create_response.json()["id"]

        # Update the assistant
        update_data = {
            "name": "Updated Assistant Name",
            "temperature": 0.5,
        }
        response = await client.patch(
            f"/api/v1/assistants/{assistant_id}", json=update_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["temperature"] == update_data["temperature"]
        # Unchanged fields should remain
        assert data["instructions"] == sample_assistant_data["instructions"]

    async def test_delete_assistant(
        self, client: AsyncClient, sample_assistant_data: dict
    ):
        """Test soft-deleting an assistant."""
        # Create an assistant first
        create_response = await client.post(
            "/api/v1/assistants", json=sample_assistant_data
        )
        assistant_id = create_response.json()["id"]

        # Delete the assistant
        response = await client.delete(f"/api/v1/assistants/{assistant_id}")
        assert response.status_code == 204

        # Verify it's soft-deleted (should not appear in list by default)
        list_response = await client.get("/api/v1/assistants")
        assert list_response.status_code == 200
        assert len(list_response.json()["assistants"]) == 0

        # Should still be accessible with include_deleted
        list_response = await client.get(
            "/api/v1/assistants", params={"include_deleted": True}
        )
        assert list_response.status_code == 200
        data = list_response.json()
        assert len(data["assistants"]) == 1
        assert data["assistants"][0]["is_deleted"] is True

    async def test_restore_assistant(
        self, client: AsyncClient, sample_assistant_data: dict
    ):
        """Test restoring a soft-deleted assistant."""
        # Create and delete an assistant
        create_response = await client.post(
            "/api/v1/assistants", json=sample_assistant_data
        )
        assistant_id = create_response.json()["id"]
        await client.delete(f"/api/v1/assistants/{assistant_id}")

        # Restore the assistant
        response = await client.post(f"/api/v1/assistants/{assistant_id}/restore")
        assert response.status_code == 200

        data = response.json()
        assert data["is_deleted"] is False

        # Should now appear in regular list
        list_response = await client.get("/api/v1/assistants")
        assert list_response.status_code == 200
        assert len(list_response.json()["assistants"]) == 1

    async def test_get_templates(self, client: AsyncClient):
        """Test getting assistant templates."""
        response = await client.get("/api/v1/assistants/templates")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # Verify template structure if any exist
        if len(data) > 0:
            template = data[0]
            assert "id" in template
            assert "name" in template
            assert "instructions" in template
