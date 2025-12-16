"""
Decorators for common ability patterns.

This module provides decorators for retry logic, timeout handling,
and rate limiting that can be applied to ability methods.
"""

import asyncio
import functools
import time
from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeVar, cast

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function

    Example:
        @retry(max_attempts=3, delay=1.0, backoff=2.0)
        async def fetch_data():
            # This will retry up to 3 times with exponential backoff
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        "Attempt failed, retrying",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        error=str(e),
                    )

                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            # All attempts failed
            logger.error(
                "All retry attempts failed", function=func.__name__, max_attempts=max_attempts
            )
            raise last_exception if last_exception else Exception("All retry attempts failed")

        return cast(Callable[..., T], wrapper)

    return decorator


def timeout(seconds: float) -> Callable:
    """
    Decorator to enforce a timeout on async functions.

    Args:
        seconds: Timeout duration in seconds

    Returns:
        Decorated function

    Raises:
        asyncio.TimeoutError: If function exceeds timeout

    Example:
        @timeout(30.0)
        async def long_operation():
            # This will raise TimeoutError if it takes more than 30 seconds
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error("Function exceeded timeout", function=func.__name__, timeout=seconds)
                raise

        return cast(Callable[..., T], wrapper)

    return decorator


class RateLimiter:
    """
    Rate limiter for controlling function call frequency.

    Uses a token bucket algorithm to enforce rate limits.
    """

    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: dict[str, list] = defaultdict(list)

    async def acquire(self, key: str) -> None:
        """
        Acquire permission to make a call.

        Args:
            key: Unique identifier for the rate limit (e.g., user_id)

        Raises:
            RuntimeError: If rate limit is exceeded
        """
        now = time.time()

        # Remove old calls outside the time window
        self.calls[key] = [
            call_time for call_time in self.calls[key] if now - call_time < self.time_window
        ]

        # Check if rate limit is exceeded
        if len(self.calls[key]) >= self.max_calls:
            oldest_call = self.calls[key][0]
            wait_time = self.time_window - (now - oldest_call)

            logger.warning(
                "Rate limit exceeded",
                key=key,
                max_calls=self.max_calls,
                time_window=self.time_window,
                wait_time=wait_time,
            )

            # Wait until we can make another call
            await asyncio.sleep(wait_time)

            # Recursive call to try again
            await self.acquire(key)
            return

        # Record this call
        self.calls[key].append(now)


def rate_limit(max_calls: int, time_window: float, key_func: Callable | None = None) -> Callable:
    """
    Decorator to enforce rate limiting on functions.

    Args:
        max_calls: Maximum number of calls allowed in time window
        time_window: Time window in seconds
        key_func: Optional function to extract rate limit key from args
                 (defaults to using first argument)

    Returns:
        Decorated function

    Example:
        @rate_limit(max_calls=10, time_window=60.0)
        async def api_call(user_id: str):
            # This will be limited to 10 calls per minute per user
            pass
    """
    limiter = RateLimiter(max_calls, time_window)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Extract rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            elif args:
                # Use first argument as key (typically user_id or similar)
                key = str(args[0])
            else:
                key = "default"

            # Acquire permission
            await limiter.acquire(key)

            # Execute function
            return await func(*args, **kwargs)

        return cast(Callable[..., T], wrapper)

    return decorator


def cancellable(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to make a function respect cancellation tokens.

    The function should periodically check if it should continue
    by checking the cancellation token.

    Args:
        func: Function to make cancellable

    Returns:
        Decorated function

    Example:
        @cancellable
        async def long_task(self):
            for i in range(100):
                if self.is_cancelled():
                    return AbilityResult(success=False, error="Cancelled")
                await asyncio.sleep(1)
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        # Check if first argument has is_cancelled method (ability instance)
        if args and hasattr(args[0], "is_cancelled"):
            ability = args[0]
            if ability.is_cancelled():
                logger.info("Function cancelled before execution", function=func.__name__)
                raise asyncio.CancelledError("Operation was cancelled")

        return await func(*args, **kwargs)

    return cast(Callable[..., T], wrapper)
