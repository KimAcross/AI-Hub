"""Simple in-memory cache with TTL support."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, TypeVar, ParamSpec
from functools import wraps

P = ParamSpec("P")
T = TypeVar("T")


class TTLCache:
    """Simple TTL-based in-memory cache."""

    def __init__(self, default_ttl_seconds: int = 300):
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._default_ttl = timedelta(seconds=default_ttl_seconds)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Get a value from cache if not expired."""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if datetime.utcnow() < expiry:
                    return value
                # Remove expired entry
                del self._cache[key]
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set a value in cache with optional custom TTL."""
        ttl = (
            timedelta(seconds=ttl_seconds)
            if ttl_seconds is not None
            else self._default_ttl
        )
        expiry = datetime.utcnow() + ttl
        async with self._lock:
            self._cache[key] = (value, expiry)

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self) -> int:
        """Remove all expired entries and return count removed."""
        now = datetime.utcnow()
        async with self._lock:
            expired_keys = [
                key for key, (_, expiry) in self._cache.items() if expiry <= now
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)


# Global cache instance
_cache = TTLCache(default_ttl_seconds=300)  # 5 minute default TTL


def cached(
    key_prefix: str,
    ttl_seconds: int = 300,
    key_builder: Callable[..., str] | None = None,
):
    """
    Decorator for caching async function results.

    Args:
        key_prefix: Prefix for the cache key
        ttl_seconds: Time-to-live in seconds
        key_builder: Optional function to build cache key from arguments
    """

    def decorator(
        func: Callable[P, Coroutine[Any, Any, T]],
    ) -> Callable[P, Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Build cache key
            if key_builder:
                cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                # Simple key from string representation of args
                key_parts = [str(a) for a in args[1:]]  # Skip self/cls
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{':'.join(key_parts) or 'default'}"

            # Check cache
            cached_value = await _cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await _cache.set(cache_key, result, ttl_seconds)
            return result

        return wrapper

    return decorator


async def get_cache() -> TTLCache:
    """Get the global cache instance."""
    return _cache


async def invalidate_cache(key_prefix: str) -> None:
    """Invalidate all cache entries with the given prefix."""
    async with _cache._lock:
        keys_to_delete = [
            key for key in _cache._cache.keys() if key.startswith(key_prefix)
        ]
        for key in keys_to_delete:
            del _cache._cache[key]
