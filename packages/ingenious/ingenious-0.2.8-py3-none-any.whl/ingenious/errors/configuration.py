"""Configuration-related error classes."""

from __future__ import annotations

from typing import Any, Optional

from ingenious.errors.base_error import IngeniousError
from ingenious.errors.enums import ErrorCategory, ErrorSeverity


class ConfigurationError(IngeniousError):
    """Base class for configuration-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize ConfigurationError with configuration-specific defaults.

        Args:
            message: Error description.
            **kwargs: Additional error context passed to IngeniousError.
        """
        kwargs.setdefault("category", ErrorCategory.CONFIGURATION)
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        kwargs.setdefault("recoverable", False)
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "There is a configuration error. Please check your settings."


class ConfigFileError(ConfigurationError):
    """Raised when configuration file operations fail."""

    def __init__(self, message: str, config_path: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize ConfigFileError with configuration file path context.

        Args:
            message: Error description.
            config_path: Path to the configuration file that failed.
            **kwargs: Additional error context passed to ConfigurationError.
        """
        if config_path:
            kwargs.setdefault("context", {}).update({"config_path": config_path})
        super().__init__(message, **kwargs)


class EnvironmentError(ConfigurationError):
    """Raised when environment variable operations fail."""

    def __init__(self, message: str, env_var: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize EnvironmentError with environment variable context.

        Args:
            message: Error description.
            env_var: Name of the environment variable that caused the error.
            **kwargs: Additional error context passed to ConfigurationError.
        """
        if env_var:
            kwargs.setdefault("context", {}).update({"env_var": env_var})
        super().__init__(message, **kwargs)


class ValidationError(ConfigurationError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ValidationError with field validation context.

        Args:
            message: Error description.
            field: Name of the field that failed validation.
            value: The value that failed validation.
            **kwargs: Additional error context passed to ConfigurationError.
        """
        if field:
            kwargs.setdefault("context", {}).update({"field": field, "value": str(value)})
        super().__init__(message, **kwargs)
