"""Error recovery strategies."""

from __future__ import annotations

import time
from typing import Any, Callable

from ingenious.core.structured_logging import get_logger
from ingenious.errors.base import IngeniousError

logger = get_logger(__name__)


class RecoveryStrategy:
    """Base class for error recovery strategies."""

    def can_recover(self, error: IngeniousError) -> bool:
        """Check if this strategy can recover from the given error."""
        raise NotImplementedError

    def recover(self, error: IngeniousError, *args: Any, **kwargs: Any) -> Any:
        """Attempt to recover from the error."""
        raise NotImplementedError


class FallbackRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy that tries fallback operations."""

    def __init__(self, fallback_functions: list[Callable[..., Any]]):
        """Initialize FallbackRecoveryStrategy with fallback operations.

        Args:
            fallback_functions: List of fallback functions to try in order for error recovery.
        """
        self.fallback_functions = fallback_functions

    def can_recover(self, error: IngeniousError) -> bool:
        """Check if fallback recovery is applicable."""
        return error.recoverable and len(self.fallback_functions) > 0

    def recover(self, error: IngeniousError, *args: Any, **kwargs: Any) -> Any:
        """Try fallback functions in order."""
        for i, fallback_func in enumerate(self.fallback_functions):
            try:
                logger.info(
                    f"Attempting recovery with fallback function {i + 1}",
                    fallback_function=fallback_func.__name__,
                    original_error=error.error_code,
                )
                return fallback_func(*args, **kwargs)

            except Exception as fallback_error:
                logger.warning(
                    f"Fallback function {i + 1} also failed",
                    fallback_function=fallback_func.__name__,
                    error=str(fallback_error),
                )
                continue

        # If all fallbacks failed, raise the original error
        raise error


class CircuitBreakerRecoveryStrategy(RecoveryStrategy):
    """Recovery strategy that implements circuit breaker pattern."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type[Exception] = IngeniousError,
    ):
        """Initialize CircuitBreakerRecoveryStrategy with circuit breaker parameters.

        Args:
            failure_threshold: Number of failures before opening the circuit.
            recovery_timeout: Timeout in seconds before attempting recovery from open state.
            expected_exception: Exception type that triggers circuit breaker logic.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

    def can_recover(self, error: IngeniousError) -> bool:
        """Check if circuit breaker should be applied."""
        return isinstance(error, self.expected_exception)

    def recover(
        self,
        error: IngeniousError,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Apply circuit breaker logic."""
        current_time = time.time()

        if self.state == "open":
            if current_time - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker transitioning to half-open state")
            else:
                raise error

        try:
            result = operation(*args, **kwargs)

            # Success - reset circuit breaker
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info("Circuit breaker closed after successful recovery")

            return result

        except self.expected_exception as exc:
            self.failure_count += 1
            self.last_failure_time = int(current_time)

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(
                    f"Circuit breaker opened after {self.failure_count} failures",
                    failure_threshold=self.failure_threshold,
                    recovery_timeout=self.recovery_timeout,
                )

            raise exc
