"""Error handling context managers and utilities.

============================================

This module provides context managers and utilities for consistent error
handling throughout the Ingenious system, including:

- Context managers for common operations
- Error recovery strategies
- Correlation ID tracking
- Retry mechanisms with exponential backoff
- Database transaction error handling

Usage Examples:

    # Database operations with auto-retry
    with database_operation("user_creation", max_retries=3):
        user = create_user(data)

    # API operations with correlation tracking
    with api_operation("chat_request") as ctx:
        response = process_chat(request)
        ctx.add_metadata(response_tokens=response.token_count)

    # File operations with proper error mapping
    with file_operation("env_load", "/path/to/.env"):
        load_environment()

The module has been refactored into a package structure for better maintainability.
All public APIs remain unchanged for backward compatibility.
"""

# Async context managers
from .async_context_managers import async_operation_context

# Context managers
from .context_managers import (
    api_operation,
    database_operation,
    file_operation,
    operation_context,
    workflow_operation,
)

# Correlation ID management
from .correlation import with_correlation_id

# Retry decorators
from .decorators import async_retry_on_error, retry_on_error

# Operation context
from .operation_context import OperationContext

# Recovery strategies
from .recovery import (
    CircuitBreakerRecoveryStrategy,
    FallbackRecoveryStrategy,
    RecoveryStrategy,
)

__all__ = [
    # Context managers
    "OperationContext",
    "operation_context",
    "database_operation",
    "api_operation",
    "file_operation",
    "workflow_operation",
    "async_operation_context",
    # Retry decorators
    "retry_on_error",
    "async_retry_on_error",
    # Recovery strategies
    "RecoveryStrategy",
    "FallbackRecoveryStrategy",
    "CircuitBreakerRecoveryStrategy",
    # Correlation ID management
    "with_correlation_id",
]
