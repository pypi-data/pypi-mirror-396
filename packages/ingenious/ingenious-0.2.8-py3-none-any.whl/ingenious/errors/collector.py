"""Error collection and reporting utilities."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from ingenious.errors.base_error import IngeniousError
from ingenious.errors.enums import ErrorCategory, ErrorSeverity


class ErrorCollector:
    """Collects and manages errors for batch processing and reporting."""

    def __init__(self) -> None:
        """Initialize ErrorCollector with empty error storage."""
        self.errors: List[IngeniousError] = []
        self.error_counts: Dict[str, int] = {}

    def add_error(self, error: IngeniousError) -> None:
        """Add an error to the collection."""
        self.errors.append(error)

        error_key = f"{error.__class__.__name__}:{error.error_code}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[IngeniousError]:
        """Get errors filtered by severity."""
        return [error for error in self.errors if error.severity == severity]

    def get_errors_by_category(self, category: ErrorCategory) -> List[IngeniousError]:
        """Get errors filtered by category."""
        return [error for error in self.errors if error.category == category]

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected errors."""
        return {
            "total_errors": len(self.errors),
            "error_counts": self.error_counts,
            "by_severity": {
                severity.value: len(self.get_errors_by_severity(severity))
                for severity in ErrorSeverity
            },
            "by_category": {
                category.value: len(self.get_errors_by_category(category))
                for category in ErrorCategory
            },
            "recoverable_errors": sum(1 for e in self.errors if e.recoverable),
            "non_recoverable_errors": sum(1 for e in self.errors if not e.recoverable),
        }

    def export_to_json(self) -> str:
        """Export error collection to JSON."""
        data = {
            "summary": self.get_summary(),
            "errors": [error.to_dict() for error in self.errors],
        }
        return json.dumps(data, indent=2, default=str)

    def clear(self) -> None:
        """Clear all collected errors."""
        self.errors.clear()
        self.error_counts.clear()
