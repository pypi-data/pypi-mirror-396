"""API-related error classes."""

from __future__ import annotations

from typing import Any, Optional

from ingenious.errors.base_error import IngeniousError
from ingenious.errors.enums import ErrorCategory, ErrorSeverity


class APIError(IngeniousError):
    """Base class for API-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize APIError with API-specific defaults.

        Args:
            message: Error description.
            **kwargs: Additional error context passed to IngeniousError.
        """
        kwargs.setdefault("category", ErrorCategory.API)
        kwargs.setdefault("severity", ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "An API error occurred. Please check your request."


class RequestValidationError(APIError):
    """Raised when API request validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize RequestValidationError with request field context.

        Args:
            message: Error description.
            field: Request field that failed validation.
            value: Invalid value that was provided.
            **kwargs: Additional error context passed to APIError.
        """
        kwargs.setdefault("severity", ErrorSeverity.LOW)
        kwargs.setdefault("recoverable", False)
        if field:
            kwargs.setdefault("context", {}).update({"field": field, "value": str(value)})
        super().__init__(message, **kwargs)


class ResponseError(APIError):
    """Raised when API response generation fails."""

    def __init__(self, message: str, response_type: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize ResponseError with response type context.

        Args:
            message: Error description.
            response_type: Type of response that failed to generate.
            **kwargs: Additional error context passed to APIError.
        """
        if response_type:
            kwargs.setdefault("context", {}).update({"response_type": response_type})
        super().__init__(message, **kwargs)


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        window: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize RateLimitError with rate limit context.

        Args:
            message: Error description.
            limit: Maximum number of requests allowed.
            window: Time window for the rate limit.
            **kwargs: Additional error context passed to APIError.
        """
        kwargs.setdefault("severity", ErrorSeverity.LOW)
        if limit:
            kwargs.setdefault("context", {}).update({"rate_limit": limit})
        if window:
            kwargs.setdefault("context", {}).update({"time_window": window})
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "Rate limit exceeded. Please try again later."
