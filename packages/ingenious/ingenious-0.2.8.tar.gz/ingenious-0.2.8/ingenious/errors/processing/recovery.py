"""Error recovery strategies."""

import time
from typing import Any, Callable, List

from ingenious.core.structured_logging import get_logger

from .base import ProcessingError
from .enums import ErrorCode

logger = get_logger(__name__)


class RecoveryStrategy:
    """Base class for error recovery strategies."""

    def can_recover(self, error: ProcessingError) -> bool:
        """Check if this strategy can recover from the given error."""
        raise NotImplementedError

    def recover(self, error: ProcessingError, *args: Any, **kwargs: Any) -> Any:
        """Attempt to recover from the error."""
        raise NotImplementedError


class FallbackEngineStrategy(RecoveryStrategy):
    """Recovery strategy that tries alternative extraction engines."""

    def __init__(self, fallback_engines: List[str]) -> None:
        """Initialize FallbackEngineStrategy with alternative engines.

        Args:
            fallback_engines: List of fallback engine names to try in order.
        """
        self.fallback_engines = fallback_engines

    def can_recover(self, error: ProcessingError) -> bool:
        """Check if engine fallback is applicable."""
        from .exceptions import ExtractionError

        return isinstance(error, ExtractionError) and error.error_code in {
            ErrorCode.ENGINE_EXECUTION_FAILED,
            ErrorCode.EXTRACTION_FAILED,
            ErrorCode.UNSUPPORTED_FORMAT,
        }

    def recover(
        self,
        error: ProcessingError,
        extract_func: Callable[..., Any],
        src: Any,
        **kwargs: Any,
    ) -> Any:
        """Try extraction with fallback engines."""
        for engine in self.fallback_engines:
            try:
                logger.info(
                    "Attempting recovery with fallback engine",
                    original_engine=error.context.engine_name,
                    fallback_engine=engine,
                    error_code=error.error_code.value,
                )
                return extract_func(src, engine=engine, **kwargs)

            except ProcessingError as fallback_error:
                logger.warning(
                    "Fallback engine also failed",
                    fallback_engine=engine,
                    error_code=fallback_error.error_code.value,
                )
                continue

        # If all fallbacks failed, raise the original error
        raise error


class RetryWithDelayStrategy(RecoveryStrategy):
    """Recovery strategy that retries after a delay."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0) -> None:
        """Initialize RetryWithDelayStrategy with retry parameters.

        Args:
            max_retries: Maximum number of retry attempts.
            base_delay: Base delay in seconds between retries (doubles with each retry).
        """
        self.max_retries = max_retries
        self.base_delay = base_delay

    def can_recover(self, error: ProcessingError) -> bool:
        """Check if retry is applicable."""
        return (
            error.recoverable
            and error.context.retry_count < self.max_retries
            and error.error_code
            in {
                ErrorCode.NETWORK_TIMEOUT,
                ErrorCode.NETWORK_CONNECTION_FAILED,
                ErrorCode.MEMORY_EXCEEDED,
            }
        )

    def recover(
        self,
        error: ProcessingError,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Retry the operation with delay."""
        delay = self.base_delay * (2**error.context.retry_count)

        logger.info(
            "Retrying operation after delay",
            retry_count=error.context.retry_count + 1,
            max_retries=self.max_retries,
            delay_seconds=delay,
        )

        time.sleep(delay)

        # Update context for next attempt
        error.context.retry_count += 1

        return operation(*args, **kwargs)
