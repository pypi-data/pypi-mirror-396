"""Error context dataclass for rich error information."""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from typing import Dict, Optional
from uuid import uuid4


@dataclass
class ErrorContext:
    """Rich context information for errors."""

    # Request tracking
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Operation details
    operation: str = ""
    component: str = ""
    workflow: Optional[str] = None
    service: Optional[str] = None

    # System state
    timestamp: float = field(default_factory=time.time)
    stack_trace: Optional[str] = None

    # Additional metadata
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        """Convert context to dictionary for logging and serialization."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None and value != "" and value != {}:
                result[key] = value
        return result

    def add_metadata(self, **kwargs: object) -> ErrorContext:
        """Add metadata to the context."""
        self.metadata.update(kwargs)
        return self

    def with_stack_trace(self) -> ErrorContext:
        """Capture and add stack trace to context."""
        self.stack_trace = traceback.format_exc()
        return self
