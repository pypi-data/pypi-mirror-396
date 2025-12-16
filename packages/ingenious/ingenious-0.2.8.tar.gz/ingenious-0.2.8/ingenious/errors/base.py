"""Comprehensive exception hierarchy for Insight Ingenious.

======================================================

This module has been refactored into separate, focused modules for better
maintainability. All public APIs remain unchanged for backward compatibility.

Exception Hierarchy:
- IngeniousError (base)
  ├── ConfigurationError
  │   ├── ConfigFileError
  │   ├── EnvironmentError
  │   └── ValidationError
  ├── DatabaseError
  │   ├── ConnectionError
  │   ├── QueryError
  │   ├── TransactionError
  │   └── MigrationError
  ├── WorkflowError
  │   ├── WorkflowNotFoundError
  │   ├── WorkflowExecutionError
  │   └── WorkflowConfigurationError
  ├── ServiceError
  │   ├── ChatServiceError
  │   ├── AuthenticationError
  │   ├── AuthorizationError
  │   └── ExternalServiceError
  ├── APIError
  │   ├── RequestValidationError
  │   ├── ResponseError
  │   └── RateLimitError
  └── ResourceError
      ├── FileNotFoundError
      ├── PermissionError
      └── StorageError

Features:
- Error codes for programmatic handling
- Rich context information
- Correlation ID support for request tracing
- Recovery strategies and retry mechanisms
- Structured logging integration
"""

from __future__ import annotations

# Import from modular structure
from ingenious.errors.api import (
    APIError,
    RateLimitError,
    RequestValidationError,
    ResponseError,
)
from ingenious.errors.base_error import IngeniousError
from ingenious.errors.collector import ErrorCollector
from ingenious.errors.configuration import (
    ConfigFileError,
    ConfigurationError,
    EnvironmentError,
    ValidationError,
)
from ingenious.errors.context import ErrorContext
from ingenious.errors.database import (
    DatabaseConnectionError,
    DatabaseError,
    DatabaseMigrationError,
    DatabaseQueryError,
    DatabaseTransactionError,
)
from ingenious.errors.enums import ErrorCategory, ErrorSeverity
from ingenious.errors.resource import (
    FileNotFoundError,
    PermissionError,
    ResourceError,
    StorageError,
)
from ingenious.errors.service import (
    AuthenticationError,
    AuthorizationError,
    ChatServiceError,
    ExternalServiceError,
    ServiceError,
)
from ingenious.errors.utilities import create_error, handle_exception
from ingenious.errors.workflow import (
    WorkflowConfigurationError,
    WorkflowError,
    WorkflowExecutionError,
    WorkflowNotFoundError,
)

__all__ = [
    # Enums
    "ErrorSeverity",
    "ErrorCategory",
    # Context and utilities
    "ErrorContext",
    "ErrorCollector",
    # Base error
    "IngeniousError",
    # Configuration errors
    "ConfigurationError",
    "ConfigFileError",
    "EnvironmentError",
    "ValidationError",
    # Database errors
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "DatabaseTransactionError",
    "DatabaseMigrationError",
    # Workflow errors
    "WorkflowError",
    "WorkflowNotFoundError",
    "WorkflowExecutionError",
    "WorkflowConfigurationError",
    # Service errors
    "ServiceError",
    "ChatServiceError",
    "AuthenticationError",
    "AuthorizationError",
    "ExternalServiceError",
    # API errors
    "APIError",
    "RequestValidationError",
    "ResponseError",
    "RateLimitError",
    # Resource errors
    "ResourceError",
    "FileNotFoundError",
    "PermissionError",
    "StorageError",
    # Convenience functions
    "create_error",
    "handle_exception",
]
