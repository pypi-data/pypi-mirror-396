"""Convenience functions for error handling."""

from __future__ import annotations

from typing import Any, Dict, Type

from ingenious.errors.base_error import IngeniousError
from ingenious.errors.configuration import ConfigurationError, ValidationError
from ingenious.errors.context import ErrorContext
from ingenious.errors.database import DatabaseConnectionError
from ingenious.errors.resource import ResourceError
from ingenious.errors.service import ExternalServiceError


def create_error(error_class: Type[IngeniousError], message: str, **kwargs: Any) -> IngeniousError:
    """Create an error instance with automatic context capture."""
    context = kwargs.get("context", ErrorContext())
    if isinstance(context, ErrorContext):
        context.with_stack_trace()

    return error_class(message, **kwargs)


def handle_exception(
    exc: Exception, operation: str = "", component: str = "", **context_kwargs: Any
) -> IngeniousError:
    """Convert a generic exception to an IngeniousError with context."""
    # Map common exception types to specific Ingenious errors
    error_mapping = {
        FileNotFoundError: ResourceError,
        PermissionError: ResourceError,
        ConnectionError: DatabaseConnectionError,
        TimeoutError: ExternalServiceError,
        ValueError: ValidationError,
        KeyError: ConfigurationError,
    }

    error_class = error_mapping.get(type(exc), IngeniousError)

    # Separate known ErrorContext fields from additional metadata
    context_fields: Dict[str, Any] = {
        "operation": operation,
        "component": component,
    }

    # Add valid ErrorContext fields if they exist in context_kwargs
    valid_fields = {
        "correlation_id",
        "request_id",
        "user_id",
        "session_id",
        "workflow",
        "service",
        "timestamp",
        "stack_trace",
    }

    metadata: Dict[str, Any] = {}
    for key, value in context_kwargs.items():
        if key in valid_fields:
            context_fields[key] = value
        else:
            metadata[key] = value

    if metadata:
        context_fields["metadata"] = metadata

    context = ErrorContext(**context_fields).with_stack_trace()

    return error_class(message=str(exc), cause=exc, context=context)  # type: ignore
