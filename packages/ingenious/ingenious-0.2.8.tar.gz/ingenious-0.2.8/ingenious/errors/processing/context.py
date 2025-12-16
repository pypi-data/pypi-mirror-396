"""Rich context information for processing errors."""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ErrorContext:
    """Rich context information for processing errors."""

    # Core context
    operation: str = ""
    component: str = ""
    timestamp: float = field(default_factory=time.time)

    # Processing details
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    engine_name: Optional[str] = None
    page_number: Optional[int] = None

    # Network details
    url: Optional[str] = None
    status_code: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None

    # System state
    memory_usage_mb: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 0

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None and value != "" and value != {}:
                result[key] = value
        return result

    def update(self, **kwargs: Any) -> "ErrorContext":
        """Update context with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.metadata[key] = value
        return self
