"""Workflow-related error classes."""

from __future__ import annotations

from typing import Any, Optional

from ingenious.errors.base_error import IngeniousError
from ingenious.errors.enums import ErrorCategory, ErrorSeverity


class WorkflowError(IngeniousError):
    """Base class for workflow-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize WorkflowError with workflow-specific defaults.

        Args:
            message: Error description.
            **kwargs: Additional error context passed to IngeniousError.
        """
        kwargs.setdefault("category", ErrorCategory.WORKFLOW)
        kwargs.setdefault("severity", ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)

    def _generate_user_message(self) -> str:
        return "A workflow error occurred. Please check your configuration."


class WorkflowNotFoundError(WorkflowError):
    """Raised when a workflow cannot be found."""

    def __init__(self, message: str, workflow_name: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize WorkflowNotFoundError with workflow name context.

        Args:
            message: Error description.
            workflow_name: Name of the workflow that could not be found.
            **kwargs: Additional error context passed to WorkflowError.
        """
        kwargs.setdefault("recoverable", False)
        if workflow_name:
            kwargs.setdefault("context", {}).update({"workflow_name": workflow_name})
        super().__init__(message, **kwargs)


class WorkflowExecutionError(WorkflowError):
    """Raised when workflow execution fails."""

    def __init__(
        self,
        message: str,
        workflow_name: Optional[str] = None,
        step: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize WorkflowExecutionError with workflow execution context.

        Args:
            message: Error description.
            workflow_name: Name of the workflow that failed.
            step: Specific workflow step that failed.
            **kwargs: Additional error context passed to WorkflowError.
        """
        if workflow_name:
            kwargs.setdefault("context", {}).update({"workflow_name": workflow_name})
        if step:
            kwargs.setdefault("context", {}).update({"workflow_step": step})
        super().__init__(message, **kwargs)


class WorkflowConfigurationError(WorkflowError):
    """Raised when workflow configuration is invalid."""

    def __init__(
        self,
        message: str,
        workflow_name: Optional[str] = None,
        config_error: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize WorkflowConfigurationError with configuration context.

        Args:
            message: Error description.
            workflow_name: Name of the workflow with invalid configuration.
            config_error: Specific configuration error details.
            **kwargs: Additional error context passed to WorkflowError.
        """
        kwargs.setdefault("recoverable", False)
        if workflow_name:
            kwargs.setdefault("context", {}).update({"workflow_name": workflow_name})
        if config_error:
            kwargs.setdefault("context", {}).update({"config_error": config_error})
        super().__init__(message, **kwargs)
