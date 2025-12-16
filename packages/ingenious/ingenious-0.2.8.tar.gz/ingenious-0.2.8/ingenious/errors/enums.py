"""Error severity and category enumerations."""

from __future__ import annotations

from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels for categorizing impact."""

    LOW = "low"  # Minor issues, system continues normally
    MEDIUM = "medium"  # Moderate issues, some functionality affected
    HIGH = "high"  # Serious issues, major functionality affected
    CRITICAL = "critical"  # System-breaking issues, immediate attention required


class ErrorCategory(Enum):
    """Error categories for classification and handling."""

    CONFIGURATION = "configuration"
    DATABASE = "database"
    WORKFLOW = "workflow"
    SERVICE = "service"
    API = "api"
    RESOURCE = "resource"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    NETWORK = "network"
    PROCESSING = "processing"
