"""Service-related error classes."""

from __future__ import annotations

from typing import Any, Optional

from ingenious.errors.base_error import IngeniousError
from ingenious.errors.enums import ErrorCategory, ErrorSeverity


class ServiceError(IngeniousError):
    """Base class for service-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize ServiceError with service-specific defaults.

        Args:
            message: Error description.
            **kwargs: Additional error context passed to IngeniousError.
        """
        kwargs.setdefault("category", ErrorCategory.SERVICE)
        kwargs.setdefault("severity", ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "A service error occurred. Please try again."


class ChatServiceError(ServiceError):
    """Raised when chat service operations fail."""

    def __init__(self, message: str, service_type: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize ChatServiceError with service type context.

        Args:
            message: Error description.
            service_type: Type of chat service that encountered the error.
            **kwargs: Additional error context passed to ServiceError.
        """
        if service_type:
            kwargs.setdefault("context", {}).update({"service_type": service_type})
        super().__init__(message, **kwargs)


class AuthenticationError(ServiceError):
    """Raised when authentication fails."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize AuthenticationError with authentication-specific defaults.

        Args:
            message: Error description.
            **kwargs: Additional error context passed to ServiceError.
        """
        kwargs.setdefault("category", ErrorCategory.AUTHENTICATION)
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        kwargs.setdefault("recoverable", False)
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "Authentication failed. Please check your credentials."


class AuthorizationError(ServiceError):
    """Raised when authorization fails."""

    def __init__(
        self, message: str, required_permission: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Initialize AuthorizationError with permission context.

        Args:
            message: Error description.
            required_permission: Permission that was required but not granted.
            **kwargs: Additional error context passed to ServiceError.
        """
        kwargs.setdefault("category", ErrorCategory.AUTHENTICATION)
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        kwargs.setdefault("recoverable", False)
        if required_permission:
            kwargs.setdefault("context", {}).update({"required_permission": required_permission})
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "You don't have permission to perform this action."


class ExternalServiceError(ServiceError):
    """Raised when external service calls fail."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ExternalServiceError with service details.

        Args:
            message: Error description.
            service_name: Name of the external service that failed.
            status_code: HTTP status code returned by the service.
            **kwargs: Additional error context passed to ServiceError.
        """
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        if service_name:
            kwargs.setdefault("context", {}).update({"service_name": service_name})
        if status_code:
            kwargs.setdefault("context", {}).update({"status_code": status_code})
        super().__init__(message, **kwargs)
