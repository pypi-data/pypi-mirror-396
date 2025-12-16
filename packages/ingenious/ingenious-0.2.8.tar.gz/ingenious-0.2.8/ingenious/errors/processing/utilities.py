"""Convenience functions for creating processing errors."""

from typing import Any, Optional

from .context import ErrorContext
from .enums import ErrorCode
from .exceptions import ExtractionError, NetworkError, ValidationError


def handle_extraction_error(
    operation: str,
    src: Any,
    engine: Optional[str] = None,
    cause: Optional[Exception] = None,
    **context_kwargs: Any,
) -> ExtractionError:
    """Create a standardized extraction error with rich context."""
    context = ErrorContext(
        operation=operation, component="document_processing.extractor", **context_kwargs
    )

    if hasattr(src, "__str__"):
        context.file_path = str(src)
    if engine:
        context.engine_name = engine

    return ExtractionError(f"Failed to {operation}", context=context, cause=cause)


def handle_network_error(
    url: str,
    operation: str = "download",
    status_code: Optional[int] = None,
    cause: Optional[Exception] = None,
    **context_kwargs: Any,
) -> NetworkError:
    """Create a standardized network error with rich context."""
    context = ErrorContext(
        operation=operation,
        component="document_processing.network",
        url=url,
        status_code=status_code,
        **context_kwargs,
    )

    error_code = ErrorCode.NETWORK_CONNECTION_FAILED
    if status_code:
        error_code = ErrorCode.HTTP_ERROR
        context.response_headers = context_kwargs.get("response_headers", {})

    return NetworkError(
        f"Network {operation} failed for {url}",
        error_code=error_code,
        context=context,
        cause=cause,
    )


def handle_validation_error(
    field_name: str, expected_type: str, actual_value: Any, **context_kwargs: Any
) -> ValidationError:
    """Create a standardized validation error."""
    context = ErrorContext(
        operation="validation",
        component="document_processing.validation",
        **context_kwargs,
    )

    return ValidationError(
        f"Validation failed for field '{field_name}': expected {expected_type}, got {type(actual_value).__name__}",
        error_code=ErrorCode.TYPE_VALIDATION_FAILED,
        context=context,
    )
