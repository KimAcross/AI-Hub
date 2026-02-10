"""Locust load testing configuration for AI-Across API."""

import json
import random
import uuid

from locust import HttpUser, TaskSet, task, between


class AssistantTasks(TaskSet):
    """Tasks for testing assistant-related endpoints."""

    assistant_ids = []

    def on_start(self):
        """Create a test assistant when starting."""
        response = self.client.post(
            "/api/v1/assistants",
            json={
                "name": f"Load Test Assistant {uuid.uuid4().hex[:8]}",
                "instructions": "You are a helpful test assistant.",
                "model": "anthropic/claude-3.5-sonnet",
            },
        )
        if response.status_code == 201:
            self.assistant_ids.append(response.json()["id"])

    @task(5)
    def list_assistants(self):
        """List all assistants."""
        self.client.get("/api/v1/assistants")

    @task(3)
    def get_assistant(self):
        """Get a specific assistant."""
        if self.assistant_ids:
            assistant_id = random.choice(self.assistant_ids)
            self.client.get(f"/api/v1/assistants/{assistant_id}")

    @task(2)
    def create_assistant(self):
        """Create a new assistant."""
        response = self.client.post(
            "/api/v1/assistants",
            json={
                "name": f"Load Test Assistant {uuid.uuid4().hex[:8]}",
                "description": "Created during load testing",
                "instructions": "You are a helpful assistant.",
                "model": "anthropic/claude-3.5-sonnet",
            },
        )
        if response.status_code == 201:
            self.assistant_ids.append(response.json()["id"])

    @task(1)
    def update_assistant(self):
        """Update an assistant."""
        if self.assistant_ids:
            assistant_id = random.choice(self.assistant_ids)
            self.client.patch(
                f"/api/v1/assistants/{assistant_id}",
                json={"description": f"Updated at {uuid.uuid4().hex[:8]}"},
            )

    @task(1)
    def get_templates(self):
        """Get assistant templates."""
        self.client.get("/api/v1/assistants/templates")


class ConversationTasks(TaskSet):
    """Tasks for testing conversation-related endpoints."""

    conversation_ids = []

    def on_start(self):
        """Create a test conversation when starting."""
        response = self.client.post(
            "/api/v1/conversations",
            json={"title": f"Load Test Conversation {uuid.uuid4().hex[:8]}"},
        )
        if response.status_code == 201:
            self.conversation_ids.append(response.json()["id"])

    @task(5)
    def list_conversations(self):
        """List all conversations."""
        self.client.get("/api/v1/conversations")

    @task(3)
    def get_conversation(self):
        """Get a specific conversation."""
        if self.conversation_ids:
            conversation_id = random.choice(self.conversation_ids)
            self.client.get(f"/api/v1/conversations/{conversation_id}")

    @task(2)
    def create_conversation(self):
        """Create a new conversation."""
        response = self.client.post(
            "/api/v1/conversations",
            json={"title": f"Load Test {uuid.uuid4().hex[:8]}"},
        )
        if response.status_code == 201:
            self.conversation_ids.append(response.json()["id"])

    @task(1)
    def update_conversation(self):
        """Update a conversation title."""
        if self.conversation_ids:
            conversation_id = random.choice(self.conversation_ids)
            self.client.patch(
                f"/api/v1/conversations/{conversation_id}",
                json={"title": f"Updated {uuid.uuid4().hex[:8]}"},
            )


class SettingsTasks(TaskSet):
    """Tasks for testing settings-related endpoints."""

    @task(5)
    def get_settings(self):
        """Get application settings."""
        self.client.get("/api/v1/settings")

    @task(1)
    def update_settings(self):
        """Update settings."""
        self.client.patch(
            "/api/v1/settings",
            json={"auto_save_interval": random.randint(0, 300)},
        )


class HealthTasks(TaskSet):
    """Tasks for testing health check endpoints."""

    @task(3)
    def health_check(self):
        """Check health endpoint."""
        self.client.get("/api/v1/health")

    @task(1)
    def readiness_check(self):
        """Check readiness endpoint."""
        self.client.get("/api/v1/ready")


class ModelsTasks(TaskSet):
    """Tasks for testing models endpoint."""

    @task(1)
    def list_models(self):
        """List available models."""
        self.client.get("/api/v1/models")


class AIAcrossUser(HttpUser):
    """Simulated user behavior for AI-Across application."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    tasks = {
        AssistantTasks: 30,
        ConversationTasks: 30,
        SettingsTasks: 20,
        HealthTasks: 15,
        ModelsTasks: 5,
    }


class APIStressUser(HttpUser):
    """High-frequency API stress testing user."""

    wait_time = between(0.1, 0.5)  # Shorter wait times for stress testing

    @task(10)
    def health_check(self):
        """Rapid health checks."""
        self.client.get("/api/v1/health")

    @task(5)
    def list_assistants(self):
        """Rapid assistant listing."""
        self.client.get("/api/v1/assistants")

    @task(5)
    def list_conversations(self):
        """Rapid conversation listing."""
        self.client.get("/api/v1/conversations")

    @task(3)
    def get_settings(self):
        """Rapid settings fetch."""
        self.client.get("/api/v1/settings")


class ReadOnlyUser(HttpUser):
    """Read-only user for testing cache effectiveness."""

    wait_time = between(0.5, 1)

    @task(10)
    def get_models(self):
        """Fetch models (should hit cache)."""
        self.client.get("/api/v1/models")

    @task(5)
    def list_assistants(self):
        """List assistants."""
        self.client.get("/api/v1/assistants")

    @task(5)
    def list_conversations(self):
        """List conversations."""
        self.client.get("/api/v1/conversations")

    @task(3)
    def get_settings(self):
        """Get settings."""
        self.client.get("/api/v1/settings")

    @task(2)
    def health_check(self):
        """Health check."""
        self.client.get("/api/v1/health")
