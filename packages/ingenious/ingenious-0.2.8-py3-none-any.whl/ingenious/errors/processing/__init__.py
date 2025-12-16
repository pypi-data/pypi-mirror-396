"""Comprehensive error handling system for document processing module.

This module provides a structured error handling framework for the document
processing pipeline with support for:

1. Hierarchical exception classes with error codes and context
2. Error recovery strategies with retry mechanisms
3. Exponential backoff decorators
4. Error reporting utilities
5. Logging integration with structured context

The error system is designed to fail gracefully while providing detailed
diagnostic information for debugging and monitoring.

Usage Example
-------------
>>> from ingenious.errors.processing import ExtractionError, retry_with_backoff
>>>
>>> @retry_with_backoff(max_retries=3, base_delay=1.0)
>>> def extract_document(file_path):
>>>     if not file_path.exists():
>>>         raise ExtractionError(
>>>             "Document not found",
>>>             error_code="DOCUMENT_NOT_FOUND",
>>>             context={"file_path": str(file_path)}
>>>         )
>>>     # ... extraction logic
"""

# Error codes and context
# Exception classes
from .base import ProcessingError
from .context import ErrorContext
from .enums import ErrorCode
from .exceptions import ExtractionError, NetworkError, ValidationError

# Retry and recovery
from .recovery import FallbackEngineStrategy, RecoveryStrategy, RetryWithDelayStrategy

# Reporting utilities
from .reporting import ErrorReporter
from .retry import retry_with_backoff

# Convenience functions
from .utilities import (
    handle_extraction_error,
    handle_network_error,
    handle_validation_error,
)

__all__ = [
    # Error codes and context
    "ErrorCode",
    "ErrorContext",
    # Exception classes
    "ProcessingError",
    "ExtractionError",
    "ValidationError",
    "NetworkError",
    # Retry and recovery
    "retry_with_backoff",
    "RecoveryStrategy",
    "FallbackEngineStrategy",
    "RetryWithDelayStrategy",
    # Reporting utilities
    "ErrorReporter",
    # Convenience functions
    "handle_extraction_error",
    "handle_network_error",
    "handle_validation_error",
]
