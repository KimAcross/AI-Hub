"""Integration tests for the conversations API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestConversationsAPI:
    """Integration tests for /api/v1/conversations endpoints."""

    async def test_create_conversation(
        self, client: AsyncClient, sample_conversation_data: dict
    ):
        """Test creating a new conversation."""
        response = await client.post(
            "/api/v1/conversations", json=sample_conversation_data
        )
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == sample_conversation_data["title"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_conversation_with_assistant(
        self,
        client: AsyncClient,
        sample_assistant_data: dict,
        sample_conversation_data: dict,
    ):
        """Test creating a conversation linked to an assistant."""
        # Create an assistant first
        assistant_response = await client.post(
            "/api/v1/assistants", json=sample_assistant_data
        )
        assistant_id = assistant_response.json()["id"]

        # Create conversation with assistant
        conversation_data = {
            **sample_conversation_data,
            "assistant_id": assistant_id,
        }
        response = await client.post("/api/v1/conversations", json=conversation_data)
        assert response.status_code == 201

        data = response.json()
        assert data["assistant_id"] == assistant_id

    async def test_create_conversation_default_title(self, client: AsyncClient):
        """Test creating a conversation without a title uses default."""
        response = await client.post("/api/v1/conversations", json={})
        assert response.status_code == 201

        data = response.json()
        assert data["title"] is not None

    async def test_list_conversations_empty(self, client: AsyncClient):
        """Test listing conversations when none exist."""
        response = await client.get("/api/v1/conversations")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_conversations(
        self, client: AsyncClient, sample_conversation_data: dict
    ):
        """Test listing conversations."""
        # Create a conversation
        await client.post("/api/v1/conversations", json=sample_conversation_data)

        response = await client.get("/api/v1/conversations")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == sample_conversation_data["title"]

    async def test_list_conversations_by_assistant(
        self,
        client: AsyncClient,
        sample_assistant_data: dict,
        sample_conversation_data: dict,
    ):
        """Test filtering conversations by assistant."""
        # Create an assistant
        assistant_response = await client.post(
            "/api/v1/assistants", json=sample_assistant_data
        )
        assistant_id = assistant_response.json()["id"]

        # Create conversation with assistant
        await client.post(
            "/api/v1/conversations",
            json={**sample_conversation_data, "assistant_id": assistant_id},
        )

        # Create conversation without assistant
        await client.post(
            "/api/v1/conversations", json={"title": "Unlinked Conversation"}
        )

        # Filter by assistant
        response = await client.get(
            "/api/v1/conversations", params={"assistant_id": assistant_id}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["assistant_id"] == assistant_id

    async def test_get_conversation(
        self, client: AsyncClient, sample_conversation_data: dict
    ):
        """Test getting a specific conversation by ID."""
        # Create a conversation
        create_response = await client.post(
            "/api/v1/conversations", json=sample_conversation_data
        )
        conversation_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/conversations/{conversation_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == conversation_id
        assert "messages" in data

    async def test_get_conversation_not_found(self, client: AsyncClient):
        """Test getting a non-existent conversation."""
        response = await client.get("/api/v1/conversations/non-existent-id")
        assert response.status_code == 404

    async def test_update_conversation(
        self, client: AsyncClient, sample_conversation_data: dict
    ):
        """Test updating a conversation title."""
        # Create a conversation
        create_response = await client.post(
            "/api/v1/conversations", json=sample_conversation_data
        )
        conversation_id = create_response.json()["id"]

        # Update the title
        new_title = "Updated Conversation Title"
        response = await client.patch(
            f"/api/v1/conversations/{conversation_id}", json={"title": new_title}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == new_title

    async def test_delete_conversation(
        self, client: AsyncClient, sample_conversation_data: dict
    ):
        """Test deleting a conversation."""
        # Create a conversation
        create_response = await client.post(
            "/api/v1/conversations", json=sample_conversation_data
        )
        conversation_id = create_response.json()["id"]

        # Delete the conversation
        response = await client.delete(f"/api/v1/conversations/{conversation_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/conversations/{conversation_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
class TestConversationExportAPI:
    """Integration tests for conversation export functionality."""

    async def test_export_conversation_markdown(
        self, client: AsyncClient, sample_conversation_data: dict
    ):
        """Test exporting a conversation as markdown."""
        # Create a conversation
        create_response = await client.post(
            "/api/v1/conversations", json=sample_conversation_data
        )
        conversation_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/conversations/{conversation_id}/export",
            params={"format": "markdown"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), str)

    async def test_export_conversation_json(
        self, client: AsyncClient, sample_conversation_data: dict
    ):
        """Test exporting a conversation as JSON."""
        # Create a conversation
        create_response = await client.post(
            "/api/v1/conversations", json=sample_conversation_data
        )
        conversation_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/conversations/{conversation_id}/export",
            params={"format": "json"},
        )
        assert response.status_code == 200
