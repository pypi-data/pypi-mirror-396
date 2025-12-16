import asyncio
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from asyncpg.exceptions import ConnectionDoesNotExistError, TooManyConnectionsError

T = TypeVar("T")


def retry_fdb_operation(max_retries: int = 2, delay: float = 1.0):
    """
    Decorator to retry database operations on connection failures.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Base delay between retries (uses exponential backoff)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionDoesNotExistError, ConnectionError) as e:
                    if isinstance(e, TooManyConnectionsError):
                        raise
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(delay * (2**attempt))  # exponential backoff
            return await func(*args, **kwargs)

        return wrapper

    return decorator
