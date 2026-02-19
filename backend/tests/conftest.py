"""Pytest configuration and fixtures for backend tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app as main_app
from app.services.admin_auth_service import get_admin_auth_service


# Test database URL - using SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign keys for SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def app(db_session: AsyncSession) -> FastAPI:
    """Create a test FastAPI application."""

    async def override_get_db():
        yield db_session

    main_app.dependency_overrides[get_db] = override_get_db
    yield main_app
    main_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    admin_token, _, _ = get_admin_auth_service().generate_token()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Admin-Token": admin_token},
    ) as client:
        yield client


@pytest.fixture
def sample_assistant_data() -> dict[str, Any]:
    """Sample data for creating an assistant."""
    return {
        "name": "Test Assistant",
        "description": "A test assistant for unit testing",
        "instructions": (
            "You are a helpful test assistant focused on concise, accurate answers. "
            "Always explain assumptions, avoid fabricated details, and ask clarifying "
            "questions when a user request is ambiguous. Keep outputs structured."
        ),
        "model": "anthropic/claude-3.5-sonnet",
        "temperature": 0.7,
        "max_tokens": 2048,
    }


@pytest.fixture
def sample_conversation_data() -> dict[str, Any]:
    """Sample data for creating a conversation."""
    return {
        "title": "Test Conversation",
    }
