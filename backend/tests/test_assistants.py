"""Tests for assistant API endpoints."""

import pytest
from httpx import AsyncClient


class TestAssistantsAPI:
    """Test suite for assistant CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_assistant(
        self,
        client: AsyncClient,
        sample_assistant_data: dict,
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

    @pytest.mark.asyncio
    async def test_create_assistant_minimal(self, client: AsyncClient):
        """Test creating an assistant with minimal data."""
        minimal_data = {
            "name": "Minimal Assistant",
            "instructions": "Be helpful.",
        }
        response = await client.post("/api/v1/assistants", json=minimal_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == minimal_data["name"]
        assert data["instructions"] == minimal_data["instructions"]
        # Check defaults are applied
        assert data["model"] == "anthropic/claude-3.5-sonnet"
        assert data["temperature"] == 0.7
        assert data["max_tokens"] == 4096

    @pytest.mark.asyncio
    async def test_create_assistant_validation_error(self, client: AsyncClient):
        """Test creating an assistant with invalid data."""
        invalid_data = {
            "name": "",  # Empty name should fail
            "instructions": "Test",
        }
        response = await client.post("/api/v1/assistants", json=invalid_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_assistants_empty(self, client: AsyncClient):
        """Test listing assistants when none exist."""
        response = await client.get("/api/v1/assistants")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_assistants(
        self,
        client: AsyncClient,
        sample_assistant_data: dict,
    ):
        """Test listing assistants."""
        # Create two assistants
        await client.post("/api/v1/assistants", json=sample_assistant_data)
        sample_assistant_data["name"] = "Second Assistant"
        await client.post("/api/v1/assistants", json=sample_assistant_data)

        response = await client.get("/api/v1/assistants")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_assistant(
        self,
        client: AsyncClient,
        sample_assistant_data: dict,
    ):
        """Test getting a specific assistant."""
        # Create an assistant
        create_response = await client.post(
            "/api/v1/assistants",
            json=sample_assistant_data,
        )
        assistant_id = create_response.json()["id"]

        # Get the assistant
        response = await client.get(f"/api/v1/assistants/{assistant_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == assistant_id
        assert data["name"] == sample_assistant_data["name"]

    @pytest.mark.asyncio
    async def test_get_assistant_not_found(self, client: AsyncClient):
        """Test getting a non-existent assistant."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/assistants/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_assistant(
        self,
        client: AsyncClient,
        sample_assistant_data: dict,
    ):
        """Test updating an assistant."""
        # Create an assistant
        create_response = await client.post(
            "/api/v1/assistants",
            json=sample_assistant_data,
        )
        assistant_id = create_response.json()["id"]

        # Update the assistant
        update_data = {
            "name": "Updated Assistant",
            "temperature": 0.9,
        }
        response = await client.patch(
            f"/api/v1/assistants/{assistant_id}",
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Assistant"
        assert data["temperature"] == 0.9
        # Other fields should remain unchanged
        assert data["instructions"] == sample_assistant_data["instructions"]

    @pytest.mark.asyncio
    async def test_delete_assistant(
        self,
        client: AsyncClient,
        sample_assistant_data: dict,
    ):
        """Test soft deleting an assistant."""
        # Create an assistant
        create_response = await client.post(
            "/api/v1/assistants",
            json=sample_assistant_data,
        )
        assistant_id = create_response.json()["id"]

        # Delete the assistant
        response = await client.delete(f"/api/v1/assistants/{assistant_id}")
        assert response.status_code == 204

        # Verify it's not in the list
        list_response = await client.get("/api/v1/assistants")
        assert len(list_response.json()) == 0

        # Verify it's in the list with include_deleted
        list_deleted_response = await client.get(
            "/api/v1/assistants",
            params={"include_deleted": True},
        )
        assert len(list_deleted_response.json()) == 1
        assert list_deleted_response.json()[0]["is_deleted"] is True

    @pytest.mark.asyncio
    async def test_restore_assistant(
        self,
        client: AsyncClient,
        sample_assistant_data: dict,
    ):
        """Test restoring a deleted assistant."""
        # Create and delete an assistant
        create_response = await client.post(
            "/api/v1/assistants",
            json=sample_assistant_data,
        )
        assistant_id = create_response.json()["id"]
        await client.delete(f"/api/v1/assistants/{assistant_id}")

        # Restore the assistant
        response = await client.post(f"/api/v1/assistants/{assistant_id}/restore")

        assert response.status_code == 200
        data = response.json()
        assert data["is_deleted"] is False

        # Verify it's back in the list
        list_response = await client.get("/api/v1/assistants")
        assert len(list_response.json()) == 1


class TestAssistantTemplates:
    """Test suite for assistant templates."""

    @pytest.mark.asyncio
    async def test_list_templates(self, client: AsyncClient):
        """Test listing assistant templates."""
        response = await client.get("/api/v1/assistants/templates")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check template structure
        template = data[0]
        assert "id" in template
        assert "name" in template
        assert "description" in template
        assert "instructions" in template
        assert "category" in template

    @pytest.mark.asyncio
    async def test_create_from_template(self, client: AsyncClient):
        """Test creating an assistant from a template."""
        # Get templates first
        templates_response = await client.get("/api/v1/assistants/templates")
        templates = templates_response.json()
        assert len(templates) > 0

        template_id = templates[0]["id"]

        # Create assistant from template
        response = await client.post(f"/api/v1/assistants/from-template/{template_id}")

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == templates[0]["name"]
        assert data["instructions"] == templates[0]["instructions"]

    @pytest.mark.asyncio
    async def test_create_from_invalid_template(self, client: AsyncClient):
        """Test creating an assistant from a non-existent template."""
        response = await client.post("/api/v1/assistants/from-template/invalid-template")

        assert response.status_code == 404
