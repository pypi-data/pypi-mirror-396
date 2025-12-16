"""Resource-related error classes."""

from __future__ import annotations

from typing import Any, Optional

from ingenious.errors.base_error import IngeniousError
from ingenious.errors.enums import ErrorCategory, ErrorSeverity


class ResourceError(IngeniousError):
    """Base class for resource-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize ResourceError with resource-specific defaults.

        Args:
            message: Error description.
            **kwargs: Additional error context passed to IngeniousError.
        """
        kwargs.setdefault("category", ErrorCategory.RESOURCE)
        kwargs.setdefault("severity", ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "A resource error occurred. Please try again."


class FileNotFoundError(ResourceError):
    """Raised when a file cannot be found."""

    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize FileNotFoundError with file path context.

        Args:
            message: Error description.
            file_path: Path to the file that could not be found.
            **kwargs: Additional error context passed to ResourceError.
        """
        kwargs.setdefault("recoverable", False)
        if file_path:
            kwargs.setdefault("context", {}).update({"file_path": file_path})
        super().__init__(message, **kwargs)


class PermissionError(ResourceError):
    """Raised when permission to access a resource is denied."""

    def __init__(self, message: str, resource_path: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize PermissionError with resource path context.

        Args:
            message: Error description.
            resource_path: Path to the resource with denied permission.
            **kwargs: Additional error context passed to ResourceError.
        """
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        kwargs.setdefault("recoverable", False)
        if resource_path:
            kwargs.setdefault("context", {}).update({"resource_path": resource_path})
        super().__init__(message, **kwargs)


class StorageError(ResourceError):
    """Raised when storage operations fail."""

    def __init__(self, message: str, storage_type: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize StorageError with storage type context.

        Args:
            message: Error description.
            storage_type: Type of storage that encountered the error.
            **kwargs: Additional error context passed to ResourceError.
        """
        if storage_type:
            kwargs.setdefault("context", {}).update({"storage_type": storage_type})
        super().__init__(message, **kwargs)
