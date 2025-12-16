"""Asynchronous context managers for operations."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from ingenious.core.structured_logging import get_logger
from ingenious.errors.base import ErrorContext, IngeniousError

from .operation_context import OperationContext

logger = get_logger(__name__)


@asynccontextmanager
async def async_operation_context(
    operation: str,
    component: str = "",
    error_class: type[IngeniousError] = IngeniousError,
    **context_kwargs: Any,
) -> AsyncGenerator[OperationContext, None]:
    """Async version of operation_context."""
    ctx = OperationContext(operation, component)

    try:
        logger.info(
            f"Starting async operation: {operation}",
            operation=operation,
            component=component,
            correlation_id=ctx.correlation_id,
            **context_kwargs,
        )

        yield ctx

        logger.info(
            f"Completed async operation: {operation}",
            operation=operation,
            component=component,
            correlation_id=ctx.correlation_id,
            duration_seconds=ctx.get_duration(),
            **ctx.metadata,
        )

    except IngeniousError:
        raise

    except Exception as exc:
        error_context = ErrorContext(
            operation=operation,
            component=component,
            correlation_id=ctx.correlation_id,
            **context_kwargs,
        ).with_stack_trace()

        error = error_class(
            message=f"Async operation '{operation}' failed: {str(exc)}",
            context=error_context,
            cause=exc,
        )

        logger.error(
            f"Async operation failed: {operation}",
            operation=operation,
            component=component,
            correlation_id=ctx.correlation_id,
            duration_seconds=ctx.get_duration(),
            error_type=type(exc).__name__,
            error_message=str(exc),
            **ctx.metadata,
        )

        raise error from exc
