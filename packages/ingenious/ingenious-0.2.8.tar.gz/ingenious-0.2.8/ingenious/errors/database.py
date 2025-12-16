"""Database-related error classes."""

from __future__ import annotations

from typing import Any, Optional

from ingenious.errors.base_error import IngeniousError
from ingenious.errors.enums import ErrorCategory, ErrorSeverity


class DatabaseError(IngeniousError):
    """Base class for database-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize DatabaseError with database-specific defaults.

        Args:
            message: Error description.
            **kwargs: Additional error context passed to IngeniousError.
        """
        kwargs.setdefault("category", ErrorCategory.DATABASE)
        kwargs.setdefault("severity", ErrorSeverity.HIGH)
        kwargs.setdefault("recoverable", True)
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "A database error occurred. Please try again in a moment."


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(
        self, message: str, connection_string: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Initialize DatabaseConnectionError with sanitized connection string.

        Args:
            message: Error description.
            connection_string: Database connection string (will be sanitized to remove sensitive info).
            **kwargs: Additional error context passed to DatabaseError.
        """
        kwargs.setdefault("severity", ErrorSeverity.CRITICAL)
        if connection_string:
            # Sanitize connection string (remove sensitive info)
            sanitized = self._sanitize_connection_string(connection_string)
            kwargs.setdefault("context", {}).update({"connection_string": sanitized})
        super().__init__(message, **kwargs)

    def _sanitize_connection_string(self, connection_string: str) -> str:
        """Remove sensitive information from connection string."""
        import re

        # Remove passwords and keys
        sanitized = re.sub(
            r"password=([^;]+)", "password=***", connection_string, flags=re.IGNORECASE
        )
        sanitized = re.sub(r"pwd=([^;]+)", "pwd=***", sanitized, flags=re.IGNORECASE)
        return sanitized


class DatabaseQueryError(DatabaseError):
    """Raised when database query execution fails."""

    def __init__(self, message: str, query: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize DatabaseQueryError with truncated query context.

        Args:
            message: Error description.
            query: SQL query that failed (will be truncated if longer than 500 characters).
            **kwargs: Additional error context passed to DatabaseError.
        """
        if query:
            # Truncate long queries
            truncated_query = query[:500] + "..." if len(query) > 500 else query
            kwargs.setdefault("context", {}).update({"query": truncated_query})
        super().__init__(message, **kwargs)


class DatabaseTransactionError(DatabaseError):
    """Raised when database transaction fails."""

    def __init__(self, message: str, transaction_id: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize DatabaseTransactionError with transaction context.

        Args:
            message: Error description.
            transaction_id: Identifier of the failed transaction.
            **kwargs: Additional error context passed to DatabaseError.
        """
        if transaction_id:
            kwargs.setdefault("context", {}).update({"transaction_id": transaction_id})
        super().__init__(message, **kwargs)


class DatabaseMigrationError(DatabaseError):
    """Raised when database migration fails."""

    def __init__(
        self, message: str, migration_version: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Initialize DatabaseMigrationError with migration version context.

        Args:
            message: Error description.
            migration_version: Version of the migration that failed.
            **kwargs: Additional error context passed to DatabaseError.
        """
        kwargs.setdefault("severity", ErrorSeverity.CRITICAL)
        kwargs.setdefault("recoverable", False)
        if migration_version:
            kwargs.setdefault("context", {}).update({"migration_version": migration_version})
        super().__init__(message, **kwargs)
