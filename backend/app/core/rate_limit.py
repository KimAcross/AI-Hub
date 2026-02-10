"""Rate limiting utilities using slowapi."""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Create limiter instance with IP-based key function
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for rate limit exceeded errors.

    Returns a JSON response with error details.
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "message": f"Rate limit exceeded: {exc.detail}",
            "retry_after": getattr(exc, "retry_after", None),
        },
    )


def get_limiter() -> Limiter:
    """Get the rate limiter instance."""
    return limiter
