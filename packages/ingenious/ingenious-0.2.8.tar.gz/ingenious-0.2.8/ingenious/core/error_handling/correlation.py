"""Correlation ID management for operations."""

from __future__ import annotations

import functools
from typing import Callable, Optional, ParamSpec, TypeVar
from uuid import uuid4

from ingenious.errors.base import IngeniousError, handle_exception

# Type variables for generic decorators
P = ParamSpec("P")
T = TypeVar("T")


def with_correlation_id(
    correlation_id: Optional[str] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to set correlation ID for an operation.

    Parameters
    ----------
    correlation_id : str, optional
        Correlation ID to use. If None, generates a new one.

    Examples:
    --------
    >>> @with_correlation_id()
    >>> def process_request(data):
    ...     # All errors in this function will have the same correlation ID
    ...     return process_data(data)
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            cid = correlation_id or str(uuid4())

            # Store correlation ID in thread-local storage or similar
            # This would integrate with your existing request context system

            try:
                return func(*args, **kwargs)
            except IngeniousError as exc:
                exc.with_correlation_id(cid)
                raise
            except Exception as exc:
                # Convert to IngeniousError with correlation ID
                error = handle_exception(exc, operation=func.__name__, component=func.__module__)
                error.with_correlation_id(cid)
                raise error from exc

        return wrapper

    return decorator
