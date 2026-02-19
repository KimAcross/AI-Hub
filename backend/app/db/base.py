"""SQLAlchemy base configuration."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Ensure all model tables are registered on Base.metadata.
from app import models  # noqa: E402,F401
