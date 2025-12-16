"""Specific exception classes for processing errors."""

from typing import Any, Dict, Optional, Union

from .base import ProcessingError
from .context import ErrorContext
from .enums import ErrorCode


class ExtractionError(ProcessingError):
    """Raised when document extraction fails.

    This error covers issues during the core document processing pipeline,
    including file I/O problems, format parsing errors, and engine failures.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Union[ErrorCode, str] = ErrorCode.EXTRACTION_FAILED,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = True,
        recovery_suggestion: Optional[str] = None,
    ):
        """Initialize ExtractionError with document extraction failure context.

        Args:
            message: Error description.
            error_code: Specific extraction error code.
            context: Additional error context information.
            cause: Original exception that triggered this error.
            recoverable: Whether the extraction can be retried with different parameters.
            recovery_suggestion: Suggestion for how to resolve the extraction failure.
        """
        if recovery_suggestion is None:
            recovery_suggestion = self._get_default_recovery_suggestion(error_code)

        super().__init__(
            message,
            error_code=error_code,
            context=context,
            cause=cause,
            recoverable=recoverable,
            recovery_suggestion=recovery_suggestion,
        )

    def _get_default_recovery_suggestion(self, error_code: Union[ErrorCode, str]) -> str:
        """Get default recovery suggestion based on error code."""
        suggestions = {
            ErrorCode.DOCUMENT_NOT_FOUND: "Verify the file path exists and is accessible",
            ErrorCode.DOCUMENT_CORRUPTED: "Try a different extraction engine or repair the document",
            ErrorCode.UNSUPPORTED_FORMAT: "Convert to a supported format or use a different engine",
            ErrorCode.MEMORY_EXCEEDED: "Reduce document size or increase available memory",
            ErrorCode.ENGINE_EXECUTION_FAILED: "Try a different extraction engine",
        }

        if isinstance(error_code, ErrorCode):
            return suggestions.get(error_code, "Check logs for specific recovery steps")

        return "Check logs for specific recovery steps"


class ValidationError(ProcessingError):
    """Raised when document content or schema validation fails.

    This error is used for issues with data validation, including schema
    mismatches, content format problems, and type checking failures.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Union[ErrorCode, str] = ErrorCode.SCHEMA_VALIDATION_FAILED,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = False,  # Validation errors usually require data fixes
        recovery_suggestion: Optional[str] = None,
    ):
        """Initialize ValidationError with validation failure context.

        Args:
            message: Error description.
            error_code: Specific validation error code.
            context: Additional error context information.
            cause: Original exception that triggered this error.
            recoverable: Whether the validation can pass with corrected data (usually False).
            recovery_suggestion: Suggestion for how to fix the validation failure.
        """
        if recovery_suggestion is None:
            recovery_suggestion = "Review and correct the input data format"

        super().__init__(
            message,
            error_code=error_code,
            context=context,
            cause=cause,
            recoverable=recoverable,
            recovery_suggestion=recovery_suggestion,
        )


class NetworkError(ProcessingError):
    """Raised when network operations fail during document processing.

    This covers download failures, timeouts, connectivity issues, and
    HTTP errors when fetching remote documents.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Union[ErrorCode, str] = ErrorCode.NETWORK_CONNECTION_FAILED,
        context: Optional[Union[ErrorContext, Dict[str, Any]]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = True,  # Network errors are often transient
        recovery_suggestion: Optional[str] = None,
    ):
        """Initialize NetworkError with network operation failure context.

        Args:
            message: Error description.
            error_code: Specific network error code.
            context: Additional error context including URL and status code.
            cause: Original exception that triggered this error.
            recoverable: Whether the operation can be retried (usually True for transient failures).
            recovery_suggestion: Suggestion for how to resolve the network issue.
        """
        if recovery_suggestion is None:
            recovery_suggestion = self._get_default_recovery_suggestion(error_code)

        super().__init__(
            message,
            error_code=error_code,
            context=context,
            cause=cause,
            recoverable=recoverable,
            recovery_suggestion=recovery_suggestion,
        )

    def _get_default_recovery_suggestion(self, error_code: Union[ErrorCode, str]) -> str:
        """Get default recovery suggestion based on error code."""
        suggestions = {
            ErrorCode.NETWORK_TIMEOUT: "Increase timeout or retry the operation",
            ErrorCode.NETWORK_CONNECTION_FAILED: "Check network connectivity and retry",
            ErrorCode.DOWNLOAD_SIZE_EXCEEDED: "Use a smaller document or increase size limits",
            ErrorCode.HTTP_ERROR: "Check URL validity and server status",
        }

        if isinstance(error_code, ErrorCode):
            return suggestions.get(error_code, "Check network connection and retry")

        return "Check network connection and retry"
