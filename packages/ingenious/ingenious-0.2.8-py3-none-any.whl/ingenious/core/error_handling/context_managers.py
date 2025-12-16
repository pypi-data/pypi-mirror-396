"""Synchronous context managers for common operations."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Generator, Optional

from ingenious.core.structured_logging import get_logger
from ingenious.errors.base import (
    APIError,
    DatabaseConnectionError,
    DatabaseError,
    ErrorContext,
    IngeniousError,
    ResourceError,
    WorkflowError,
)

from .operation_context import OperationContext

logger = get_logger(__name__)


@contextmanager
def operation_context(
    operation: str,
    component: str = "",
    error_class: type[IngeniousError] = IngeniousError,
    **context_kwargs: Any,
) -> Generator[OperationContext, None, None]:
    """Generic operation context manager with error handling.

    Parameters
    ----------
    operation : str
        Name of the operation being performed
    component : str
        Component performing the operation
    error_class : Type[IngeniousError]
        Error class to use for wrapping exceptions
    **context_kwargs
        Additional context to include in errors

    Yields:
    ------
    OperationContext
        Context object for the operation

    Examples:
    --------
    >>> with operation_context("user_lookup", "auth_service") as ctx:
    ...     user = find_user(user_id)
    ...     ctx.add_metadata(user_found=user is not None)
    """
    ctx = OperationContext(operation, component)

    try:
        logger.info(
            f"Starting operation: {operation}",
            operation=operation,
            component=component,
            correlation_id=ctx.correlation_id,
            **context_kwargs,
        )

        yield ctx

        logger.info(
            f"Completed operation: {operation}",
            operation=operation,
            component=component,
            correlation_id=ctx.correlation_id,
            duration_seconds=ctx.get_duration(),
            **ctx.metadata,
        )

    except IngeniousError:
        # Re-raise Ingenious errors as-is
        raise

    except Exception as exc:
        # Convert generic exceptions to Ingenious errors
        error_context = ErrorContext(
            operation=operation,
            component=component,
            correlation_id=ctx.correlation_id,
            **context_kwargs,
        ).with_stack_trace()

        error = error_class(
            message=f"Operation '{operation}' failed: {str(exc)}",
            context=error_context,
            cause=exc,
        )

        logger.error(
            f"Operation failed: {operation}",
            operation=operation,
            component=component,
            correlation_id=ctx.correlation_id,
            duration_seconds=ctx.get_duration(),
            error_type=type(exc).__name__,
            error_message=str(exc),
            **ctx.metadata,
        )

        raise error from exc


@contextmanager
def database_operation(
    operation: str,
    table: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> Generator[OperationContext, None, None]:
    """Context manager for database operations with retry logic.

    Parameters
    ----------
    operation : str
        Database operation being performed
    table : str, optional
        Database table being accessed
    max_retries : int
        Maximum number of retry attempts
    retry_delay : float
        Delay between retries in seconds

    Examples:
    --------
    >>> with database_operation("user_create", "users", max_retries=3):
    ...     user = db.create_user(user_data)
    """
    context_kwargs = {}
    if table:
        context_kwargs["table"] = table

    for attempt in range(max_retries + 1):
        try:
            with operation_context(
                operation=operation,
                component="database",
                error_class=DatabaseError,
                attempt=attempt + 1,
                max_retries=max_retries,
                **context_kwargs,
            ) as ctx:
                yield ctx
                return  # Success, exit retry loop

        except DatabaseConnectionError as exc:
            if attempt >= max_retries:
                raise

            logger.warning(
                f"Database connection failed, retrying ({attempt + 1}/{max_retries})",
                operation=operation,
                attempt=attempt + 1,
                max_retries=max_retries,
                retry_delay=retry_delay,
                error=str(exc),
            )

            time.sleep(retry_delay * (2**attempt))  # Exponential backoff

        except DatabaseError:
            # Don't retry non-connection database errors
            raise


@contextmanager
def api_operation(
    operation: str, endpoint: Optional[str] = None, method: Optional[str] = None
) -> Generator[OperationContext, None, None]:
    """Context manager for API operations.

    Parameters
    ----------
    operation : str
        API operation being performed
    endpoint : str, optional
        API endpoint being called
    method : str, optional
        HTTP method being used

    Examples:
    --------
    >>> with api_operation("chat_request", "/api/v1/chat", "POST") as ctx:
    ...     response = process_chat_request(request)
    ...     ctx.add_metadata(response_tokens=response.token_count)
    """
    context_kwargs = {}
    if endpoint:
        context_kwargs["endpoint"] = endpoint
    if method:
        context_kwargs["method"] = method

    with operation_context(
        operation=operation, component="api", error_class=APIError, **context_kwargs
    ) as ctx:
        yield ctx


@contextmanager
def file_operation(
    operation: str, file_path: str, required: bool = True
) -> Generator[OperationContext, None, None]:
    """Context manager for file operations.

    Parameters
    ----------
    operation : str
        File operation being performed
    file_path : str
        Path to the file being accessed
    required : bool
        Whether the file is required to exist

    Examples:
    --------
    >>> with file_operation("env_load", "/path/to/.env"):
    ...     load_environment()
    """
    try:
        with operation_context(
            operation=operation,
            component="filesystem",
            error_class=ResourceError,
            file_path=file_path,
            required=required,
        ) as ctx:
            yield ctx

    except (FileNotFoundError, PermissionError, OSError) as exc:
        # Map filesystem errors to appropriate Ingenious errors
        error_context = (
            ErrorContext(operation=operation, component="filesystem")
            .with_stack_trace()
            .add_metadata(file_path=file_path)
        )

        if isinstance(exc, FileNotFoundError):
            error = ResourceError(
                message=f"File not found: {file_path}",
                context=error_context,
                cause=exc,
                recoverable=not required,
            )
        elif isinstance(exc, PermissionError):
            error = ResourceError(
                message=f"Permission denied accessing file: {file_path}",
                context=error_context,
                cause=exc,
                recoverable=False,
            )
        else:
            error = ResourceError(
                message=f"File operation failed: {str(exc)}",
                context=error_context,
                cause=exc,
            )

        raise error from exc


@contextmanager
def workflow_operation(
    workflow_name: str, operation: str, step: Optional[str] = None
) -> Generator[OperationContext, None, None]:
    """Context manager for workflow operations.

    Parameters
    ----------
    workflow_name : str
        Name of the workflow being executed
    operation : str
        Specific operation within the workflow
    step : str, optional
        Current step in the workflow

    Examples:
    --------
    >>> with workflow_operation("chat_flow", "process_message", "validation"):
    ...     validate_message(message)
    """
    context_kwargs = {"workflow_name": workflow_name}
    if step:
        context_kwargs["workflow_step"] = step

    with operation_context(
        operation=operation,
        component="workflow",
        error_class=WorkflowError,
        **context_kwargs,
    ) as ctx:
        yield ctx
