"""Operation context for tracking state and metadata."""

from __future__ import annotations

import time
from typing import Optional
from uuid import uuid4

from ingenious.core.structured_logging import get_request_id
from ingenious.errors.base import IngeniousError


class OperationContext:
    """Context for tracking operation state and metadata."""

    def __init__(self, operation: str, component: str = "", correlation_id: Optional[str] = None):
        """Initialize OperationContext for tracking operation state and metadata.

        Args:
            operation: Name of the operation being tracked.
            component: Component name performing the operation.
            correlation_id: Unique identifier for correlating related operations. Auto-generated if not provided.
        """
        self.operation = operation
        self.component = component
        self.correlation_id = correlation_id or str(uuid4())
        self.start_time = time.time()
        self.metadata: dict[str, object] = {}
        self.errors: list[IngeniousError] = []

        # Get request context if available
        request_id = get_request_id()
        if request_id:
            self.correlation_id = request_id

    def add_metadata(self, **kwargs: object) -> "OperationContext":
        """Add metadata to the operation context."""
        self.metadata.update(kwargs)
        return self

    def add_error(self, error: IngeniousError) -> None:
        """Add an error to the operation context."""
        error.with_correlation_id(self.correlation_id)
        self.errors.append(error)

    def get_duration(self) -> float:
        """Get operation duration in seconds."""
        return time.time() - self.start_time
