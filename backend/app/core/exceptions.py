"""Custom exceptions for AI-Across application."""


class AIAcrossException(Exception):
    """Base exception for AI-Across application."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(AIAcrossException):
    """Base exception for resource not found errors."""

    pass


class ValidationError(AIAcrossException):
    """Base exception for validation errors."""

    pass


class AuthenticationError(AIAcrossException):
    """Base exception for authentication errors."""

    pass


class AuthorizationError(AIAcrossException):
    """Base exception for authorization errors."""

    pass


class QuotaExceededError(AIAcrossException):
    """Raised when usage quota is exceeded."""

    def __init__(self, reason: str):
        super().__init__(f"Quota exceeded: {reason}")


class AssistantNotFoundError(AIAcrossException):
    """Raised when an assistant is not found."""

    def __init__(self, assistant_id: str):
        super().__init__(f"Assistant not found: {assistant_id}")


class FileNotFoundError(AIAcrossException):
    """Raised when a knowledge file is not found."""

    def __init__(self, file_id: str):
        super().__init__(f"File not found: {file_id}")


class ConversationNotFoundError(AIAcrossException):
    """Raised when a conversation is not found."""

    def __init__(self, conversation_id: str):
        super().__init__(f"Conversation not found: {conversation_id}")


class FileProcessingError(AIAcrossException):
    """Raised when file processing fails."""

    def __init__(self, filename: str, reason: str):
        super().__init__(f"Failed to process file '{filename}': {reason}")


class InvalidFileTypeError(AIAcrossException):
    """Raised when an unsupported file type is uploaded."""

    def __init__(self, file_type: str):
        super().__init__(f"Unsupported file type: {file_type}")


class FileTooLargeError(AIAcrossException):
    """Raised when a file exceeds the maximum size."""

    def __init__(self, filename: str, max_size_mb: int):
        super().__init__(f"File '{filename}' exceeds maximum size of {max_size_mb}MB")


class OpenRouterError(AIAcrossException):
    """Raised when OpenRouter API returns an error."""

    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(f"OpenRouter API error: {message}")


class RAGRetrievalError(AIAcrossException):
    """Raised when RAG retrieval fails."""

    def __init__(self, reason: str):
        super().__init__(f"RAG retrieval failed: {reason}")


class SettingsError(AIAcrossException):
    """Raised when there's an issue with settings."""

    def __init__(self, key: str, reason: str):
        super().__init__(f"Settings error for '{key}': {reason}")
