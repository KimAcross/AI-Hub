"""Structured logging with request context propagation."""

import contextvars
import logging
import sys
from typing import Any

from pythonjsonlogger.json import JsonFormatter

from app.core.config import get_settings

request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
user_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "user_id", default=None
)
conversation_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "conversation_id", default=None
)
assistant_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "assistant_id", default=None
)


class ContextFilter(logging.Filter):
    """Inject contextvars into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        record.user_id = user_id_ctx.get()
        record.conversation_id = conversation_id_ctx.get()
        record.assistant_id = assistant_id_ctx.get()
        return True


def set_request_context(
    *,
    request_id: str | None = None,
    user_id: str | None = None,
    conversation_id: str | None = None,
    assistant_id: str | None = None,
) -> None:
    """Set context variables for the current async task."""
    if request_id is not None:
        request_id_ctx.set(request_id)
    if user_id is not None:
        user_id_ctx.set(user_id)
    if conversation_id is not None:
        conversation_id_ctx.set(conversation_id)
    if assistant_id is not None:
        assistant_id_ctx.set(assistant_id)


def clear_request_context() -> None:
    """Clear contextvars at request boundaries."""
    request_id_ctx.set(None)
    user_id_ctx.set(None)
    conversation_id_ctx.set(None)
    assistant_id_ctx.set(None)


def configure_logging() -> None:
    """Configure root logging once at startup."""
    settings = get_settings()
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(settings.log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())

    if settings.log_format.lower() == "json":
        formatter: logging.Formatter = JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s "
            "%(request_id)s %(user_id)s %(conversation_id)s %(assistant_id)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s "
            "[request_id=%(request_id)s user_id=%(user_id)s "
            "conversation_id=%(conversation_id)s assistant_id=%(assistant_id)s] "
            "%(message)s"
        )

    handler.setFormatter(formatter)
    root.addHandler(handler)


def get_logger(name: str, **fields: Any) -> logging.LoggerAdapter:
    """Get a logger adapter that merges structured extra fields."""
    return logging.LoggerAdapter(logging.getLogger(name), extra=fields)
