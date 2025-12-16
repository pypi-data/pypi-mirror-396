"""Base exception class for all Ingenious-specific errors."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Union

from ingenious.core.structured_logging import get_logger
from ingenious.errors.context import ErrorContext
from ingenious.errors.enums import ErrorCategory, ErrorSeverity

logger = get_logger(__name__)


class IngeniousError(Exception):
    """Base exception class for all Ingenious-specific errors.

    This class provides a standardized interface for error handling with:
    - Structured error codes and categories
    - Rich context information with correlation IDs
    - Automatic logging integration
    - Recovery suggestions
    - Error severity classification
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        category: ErrorCategory = ErrorCategory.PROCESSING,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = True,
        recovery_suggestion: Optional[str] = None,
        user_message: Optional[str] = None,
    ):
        """Initialize Ingenious error.

        Parameters
        ----------
        message : str
            Technical error description for developers
        error_code : str, optional
            Unique error code for programmatic handling
        category : ErrorCategory
            Error category for classification
        severity : ErrorSeverity
            Error severity level
        context : ErrorContext or dict, optional
            Additional context information
        cause : Exception, optional
            Original exception that triggered this error
        recoverable : bool, default=True
            Whether this error can potentially be recovered from
        recovery_suggestion : str, optional
            Suggestion for how to recover from this error
        user_message : str, optional
            User-friendly error message
        """
        super().__init__(message)

        self.message = message
        self.error_code = error_code or self._generate_error_code()
        self.category = category
        self.severity = severity
        self.cause = cause
        self.recoverable = recoverable
        self.recovery_suggestion = recovery_suggestion
        self.user_message = user_message or self._generate_user_message()

        # Handle context
        if context is None:
            self.context = ErrorContext()
        elif isinstance(context, dict):
            self.context = ErrorContext(
                **{k: v for k, v in context.items() if k in ErrorContext.__dataclass_fields__}
            )
            self.context.metadata.update(
                {k: v for k, v in context.items() if k not in ErrorContext.__dataclass_fields__}
            )
        else:
            self.context = context

        # Set component from class name if not provided
        if not self.context.component:
            self.context.component = self.__class__.__module__

        # Log the error
        self._log_error()

    def _generate_error_code(self) -> str:
        """Generate a default error code based on class name."""
        class_name = self.__class__.__name__
        # Convert CamelCase to UPPER_SNAKE_CASE
        import re

        return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()

    def _generate_user_message(self) -> str:
        """Generate a user-friendly message."""
        return "An error occurred while processing your request. Please try again."

    def _log_error(self) -> None:
        """Log the error with structured context."""
        log_data = {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "recoverable": self.recoverable,
            **self.context.to_dict(),
        }

        if self.cause:
            log_data["cause"] = str(self.cause)
            log_data["cause_type"] = self.cause.__class__.__name__

        if self.recovery_suggestion:
            log_data["recovery_suggestion"] = self.recovery_suggestion

        # Log with appropriate level based on severity
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical("Critical error occurred", **log_data)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error("High severity error occurred", **log_data)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning("Medium severity error occurred", **log_data)
        else:
            logger.info("Low severity error occurred", **log_data)

    def with_context(self, **kwargs: Any) -> IngeniousError:
        """Add additional context to the error."""
        self.context.add_metadata(**kwargs)
        return self

    def with_correlation_id(self, correlation_id: str) -> IngeniousError:
        """Set correlation ID for request tracing."""
        self.context.correlation_id = correlation_id
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "user_message": self.user_message,
            "recoverable": self.recoverable,
            "recovery_suggestion": self.recovery_suggestion,
            "context": self.context.to_dict(),
            "cause": str(self.cause) if self.cause else None,
        }

    def to_json(self) -> str:
        """Convert error to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
