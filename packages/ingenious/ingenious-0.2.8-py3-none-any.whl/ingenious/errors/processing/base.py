"""Base exception for all document processing errors."""

from typing import Any, Dict, Optional, Union

from ingenious.core.structured_logging import get_logger

from .context import ErrorContext
from .enums import ErrorCode

logger = get_logger(__name__)


class ProcessingError(Exception):
    """Base exception for all document processing errors.

    This class provides a standardized interface for error handling with:
    - Structured error codes
    - Rich context information
    - Recovery suggestions
    - Logging integration
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Union[ErrorCode, str] = ErrorCode.UNKNOWN_ERROR,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = True,
        recovery_suggestion: Optional[str] = None,
    ):
        """Initialize processing error.

        Parameters
        ----------
        message : str
            Human-readable error description
        error_code : ErrorCode or str
            Standardized error code for programmatic handling
        context : ErrorContext or dict, optional
            Additional context information
        cause : Exception, optional
            Original exception that triggered this error
        recoverable : bool, default=True
            Whether this error can potentially be recovered from
        recovery_suggestion : str, optional
            Suggestion for how to recover from this error
        """
        super().__init__(message)

        self.message = message
        self.error_code = error_code if isinstance(error_code, ErrorCode) else ErrorCode(error_code)
        self.cause = cause
        self.recoverable = recoverable
        self.recovery_suggestion = recovery_suggestion

        # Handle context
        if context is None:
            self.context = ErrorContext()
        elif isinstance(context, dict):
            self.context = ErrorContext(**context)
        else:
            self.context = context

        # Log the error
        self._log_error()

    def _log_error(self) -> None:
        """Log the error with structured context."""
        log_data = {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code.value,
            "message": self.message,
            "recoverable": self.recoverable,
            **self.context.to_dict(),
        }

        if self.cause:
            log_data["cause"] = str(self.cause)
            log_data["cause_type"] = self.cause.__class__.__name__

        if self.recovery_suggestion:
            log_data["recovery_suggestion"] = self.recovery_suggestion

        logger.error("Processing error occurred", **log_data)

    def with_context(self, **kwargs: Any) -> "ProcessingError":
        """Add additional context to the error."""
        self.context.update(**kwargs)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code.value,
            "message": self.message,
            "recoverable": self.recoverable,
            "recovery_suggestion": self.recovery_suggestion,
            "context": self.context.to_dict(),
            "cause": str(self.cause) if self.cause else None,
        }
