"""Structured logging with request correlation IDs."""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Optional

from pythonjsonlogger import jsonlogger

# Context variables for request-scoped data
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
conversation_id_var: ContextVar[Optional[str]] = ContextVar("conversation_id", default=None)
assistant_id_var: ContextVar[Optional[str]] = ContextVar("assistant_id", default=None)


class ContextAwareJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter that injects context variables into every log record."""

    def add_fields(
        self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record["timestamp"] = self.formatTime(record)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name

        # Inject context variables when available
        if request_id := request_id_var.get():
            log_record["request_id"] = request_id
        if user_id := user_id_var.get():
            log_record["user_id"] = user_id
        if conv_id := conversation_id_var.get():
            log_record["conversation_id"] = conv_id
        if asst_id := assistant_id_var.get():
            log_record["assistant_id"] = asst_id


class ContextAwareTextFormatter(logging.Formatter):
    """Text formatter that prepends context variables for development readability."""

    def format(self, record: logging.LogRecord) -> str:
        parts = []
        if request_id := request_id_var.get():
            parts.append(f"req={request_id[:8]}")
        if user_id := user_id_var.get():
            parts.append(f"user={user_id[:8]}")
        if conv_id := conversation_id_var.get():
            parts.append(f"conv={conv_id[:8]}")
        if asst_id := assistant_id_var.get():
            parts.append(f"asst={asst_id[:8]}")

        ctx = f" [{' '.join(parts)}]" if parts else ""
        base = f"%(asctime)s %(levelname)-8s %(name)s{ctx} %(message)s"
        formatter = logging.Formatter(base)
        return formatter.format(record)


def setup_logging(log_level: str = "INFO", log_format: str = "text") -> None:
    """Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Log format — "json" for structured JSON, "text" for human-readable.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if log_format.lower() == "json":
        formatter = ContextAwareJsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        )
    else:
        formatter = ContextAwareTextFormatter()

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


def generate_request_id() -> str:
    """Generate a new request ID."""
    return str(uuid.uuid4())
