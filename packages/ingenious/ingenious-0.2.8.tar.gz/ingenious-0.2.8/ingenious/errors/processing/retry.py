"""Retry decorator with exponential backoff for processing errors."""

import functools
import random
import time
from typing import Any, Callable, Tuple, Type, TypeVar

from ingenious.core.structured_logging import get_logger

from .base import ProcessingError

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (ProcessingError,),
    only_recoverable: bool = True,
) -> Callable[[F], F]:
    """Decorator that retries function execution with exponential backoff.

    Parameters
    ----------
    max_retries : int, default=3
        Maximum number of retry attempts
    base_delay : float, default=1.0
        Initial delay between retries in seconds
    max_delay : float, default=60.0
        Maximum delay between retries in seconds
    exponential_base : float, default=2.0
        Base for exponential backoff calculation
    jitter : bool, default=True
        Whether to add random jitter to delays
    exceptions : tuple of Exception types, default=(ProcessingError,)
        Exception types that should trigger retries
    only_recoverable : bool, default=True
        Only retry recoverable ProcessingError instances

    Returns:
    -------
    Callable
        Decorated function with retry logic

    Examples:
    --------
    >>> @retry_with_backoff(max_retries=3, base_delay=1.0)
    >>> def fetch_document(url):
    >>>     response = requests.get(url)
    >>>     if response.status_code != 200:
    >>>         raise NetworkError("Download failed", error_code=ErrorCode.HTTP_ERROR)
    >>>     return response.content
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as exc:
                    last_exception = exc

                    # Check if we should retry this exception
                    should_retry = True
                    if isinstance(exc, ProcessingError) and only_recoverable:
                        should_retry = exc.recoverable

                    # Don't retry on the last attempt or non-recoverable errors
                    if attempt >= max_retries or not should_retry:
                        # Update context with retry information
                        if isinstance(exc, ProcessingError):
                            exc.with_context(retry_count=attempt, max_retries=max_retries)
                            exc.context.metadata["final_attempt"] = True
                        raise exc

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= 0.5 + random.random() * 0.5

                    # Log retry attempt
                    logger.warning(
                        "Retrying after error",
                        function_name=func.__name__,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        delay_seconds=delay,
                        exception_type=exc.__class__.__name__,
                        error_message=str(exc),
                    )

                    # Update context with retry information
                    if isinstance(exc, ProcessingError):
                        exc.with_context(
                            retry_count=attempt + 1,
                            max_retries=max_retries,
                            next_delay_seconds=delay,
                        )

                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            else:
                raise ProcessingError("Retry loop completed without success or exception")

        return wrapper  # type: ignore

    return decorator
