"""Error reporting utilities."""

import json
from typing import Any, Dict, List

from .base import ProcessingError


class ErrorReporter:
    """Utility for collecting and reporting processing errors."""

    def __init__(self) -> None:
        """Initialize ErrorReporter with empty error collection."""
        self.errors: List[ProcessingError] = []
        self.error_counts: Dict[str, int] = {}

    def add_error(self, error: ProcessingError) -> None:
        """Add an error to the collection."""
        self.errors.append(error)

        error_key = f"{error.__class__.__name__}:{error.error_code.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected errors."""
        return {
            "total_errors": len(self.errors),
            "error_counts": self.error_counts,
            "recoverable_errors": sum(1 for e in self.errors if e.recoverable),
            "non_recoverable_errors": sum(1 for e in self.errors if not e.recoverable),
            "most_common_errors": sorted(
                self.error_counts.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    def export_to_json(self) -> str:
        """Export error collection to JSON."""
        data = {
            "summary": self.get_error_summary(),
            "errors": [error.to_dict() for error in self.errors],
        }
        return json.dumps(data, indent=2, default=str)

    def clear(self) -> None:
        """Clear all collected errors."""
        self.errors.clear()
        self.error_counts.clear()
