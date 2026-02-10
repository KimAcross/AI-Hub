"""Database session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from app.core.config import get_settings

settings = get_settings()

# Determine pool class based on environment
# Use NullPool for testing, AsyncAdaptedQueuePool for production
pool_class = NullPool if settings.app_env == "testing" else AsyncAdaptedQueuePool

# Create async engine with connection pooling optimization
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    poolclass=pool_class,
    # Connection pool settings for production
    pool_size=10,  # Base number of connections
    max_overflow=20,  # Maximum overflow connections
    pool_timeout=30,  # Seconds to wait for a connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Verify connection validity before use
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
