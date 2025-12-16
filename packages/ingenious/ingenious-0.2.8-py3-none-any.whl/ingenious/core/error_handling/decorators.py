"""Retry decorators with exponential backoff."""

from __future__ import annotations

import asyncio
import functools
import random
import time
from typing import Callable, ParamSpec, TypeVar

from ingenious.core.structured_logging import get_logger
from ingenious.errors.base import IngeniousError

logger = get_logger(__name__)

# Type variables for generic decorators
P = ParamSpec("P")
T = TypeVar("T")


class _RetryHandler:
    """Shared retry logic for sync and async decorators.

    This class encapsulates the common retry behavior including:
    - Exponential backoff calculation with optional jitter
    - Exception handling and retry decision logic
    - Context updates for IngeniousError instances
    - Logging of retry attempts
    """

    def __init__(
        self,
        max_retries: int,
        base_delay: float,
        max_delay: float,
        exponential_base: float,
        jitter: bool,
        exceptions: tuple[type[Exception], ...],
        only_recoverable: bool,
        func_name: str,
    ) -> None:
        """Initialize retry handler with configuration."""
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions = exceptions
        self.only_recoverable = only_recoverable
        self.func_name = func_name

    def should_retry(self, exc: Exception, attempt: int) -> bool:
        """Determine if the operation should be retried.

        Args:
            exc: The exception that was raised
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False if should raise
        """
        # Check recoverable flag for IngeniousError
        if isinstance(exc, IngeniousError) and self.only_recoverable:
            if not exc.recoverable:
                return False

        # Don't retry on last attempt
        return attempt < self.max_retries

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for next retry with exponential backoff.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds before next retry
        """
        delay = min(self.base_delay * (self.exponential_base**attempt), self.max_delay)

        # Add jitter to prevent thundering herd
        if self.jitter:
            delay *= 0.5 + random.random() * 0.5  # nosec B311

        return delay

    def handle_final_failure(self, exc: Exception, attempt: int) -> None:
        """Update exception context for final failure.

        Args:
            exc: The exception being raised
            attempt: Final attempt number
        """
        if isinstance(exc, IngeniousError):
            exc.with_context(
                retry_count=attempt,
                max_retries=self.max_retries,
                final_attempt=True,
            )

    def log_retry(self, exc: Exception, attempt: int, delay: float, is_async: bool = False) -> None:
        """Log retry attempt.

        Args:
            exc: The exception that triggered the retry
            attempt: Current attempt number (0-indexed)
            delay: Delay before next retry
            is_async: Whether this is an async operation
        """
        prefix = "async " if is_async else ""
        logger.warning(
            f"Retrying {prefix}{self.func_name} after error",
            function_name=self.func_name,
            attempt=attempt + 1,
            max_retries=self.max_retries,
            delay_seconds=delay,
            exception_type=exc.__class__.__name__,
            error_message=str(exc),
        )

    def update_retry_context(self, exc: Exception, attempt: int, delay: float) -> None:
        """Update exception context with retry information.

        Args:
            exc: The exception being retried
            attempt: Current attempt number (0-indexed)
            delay: Delay before next retry
        """
        if isinstance(exc, IngeniousError):
            exc.with_context(
                retry_count=attempt + 1,
                max_retries=self.max_retries,
                next_delay_seconds=delay,
            )


def retry_on_error(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (IngeniousError,),
    only_recoverable: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for retrying operations on error.

    Parameters
    ----------
    max_retries : int
        Maximum number of retry attempts
    base_delay : float
        Initial delay between retries
    max_delay : float
        Maximum delay between retries
    exponential_base : float
        Base for exponential backoff
    jitter : bool
        Whether to add random jitter to delays
    exceptions : tuple
        Exception types that should trigger retries
    only_recoverable : bool
        Only retry recoverable IngeniousError instances

    Examples:
    --------
    >>> @retry_on_error(max_retries=3, base_delay=1.0)
    >>> def fetch_external_data():
    ...     # This will retry up to 3 times on IngeniousError
    ...     return api_client.get_data()
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        handler = _RetryHandler(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            exceptions=exceptions,
            only_recoverable=only_recoverable,
            func_name=func.__name__,
        )

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as exc:
                    last_exception = exc

                    if not handler.should_retry(exc, attempt):
                        handler.handle_final_failure(exc, attempt)
                        raise exc

                    delay = handler.calculate_delay(attempt)
                    handler.log_retry(exc, attempt, delay, is_async=False)
                    handler.update_retry_context(exc, attempt, delay)
                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise IngeniousError("Retry loop completed without success or exception")

        return wrapper

    return decorator


def async_retry_on_error(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (IngeniousError,),
    only_recoverable: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Async decorator for retrying operations on error.

    Parameters
    ----------
    max_retries : int
        Maximum number of retry attempts
    base_delay : float
        Initial delay between retries
    max_delay : float
        Maximum delay between retries
    exponential_base : float
        Base for exponential backoff
    jitter : bool
        Whether to add random jitter to delays
    exceptions : tuple
        Exception types that should trigger retries
    only_recoverable : bool
        Only retry recoverable IngeniousError instances

    Examples:
    --------
    >>> @async_retry_on_error(max_retries=3, base_delay=1.0)
    >>> async def fetch_external_data():
    ...     # This will retry up to 3 times on IngeniousError
    ...     return await api_client.get_data()
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        handler = _RetryHandler(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            exceptions=exceptions,
            only_recoverable=only_recoverable,
            func_name=func.__name__,
        )

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)  # type: ignore[misc, no-any-return]

                except exceptions as exc:
                    last_exception = exc

                    if not handler.should_retry(exc, attempt):
                        handler.handle_final_failure(exc, attempt)
                        raise exc

                    delay = handler.calculate_delay(attempt)
                    handler.log_retry(exc, attempt, delay, is_async=True)
                    handler.update_retry_context(exc, attempt, delay)
                    await asyncio.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise IngeniousError("Async retry loop completed without success or exception")

        return wrapper  # type: ignore[return-value]

    return decorator
