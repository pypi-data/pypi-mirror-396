"""Content filter error exception.

This module defines exceptions raised when content violates content filter policies.
"""

from typing import Any, Dict, Optional


class ContentFilterError(Exception):
    """Exception raised when user message violates OpenAI content filter.

    Attributes:
        DEFAULT_MESSAGE (str): Default error message for filter violations.
        message (str): Error message describing the violation.
        content_filter_results (Dict[str, Any]): Details about what triggered the filter.
    """

    DEFAULT_MESSAGE = (
        "The users prompt violates the content filter, please start a new conversation."
    )

    def __init__(
        self,
        message: str = DEFAULT_MESSAGE,
        content_filter_results: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize content filter error.

        Args:
            message (str): Error message, defaults to DEFAULT_MESSAGE.
            content_filter_results (Optional[Dict[str, Any]]): Filter violation details.
        """
        self.message = message
        self.content_filter_results = content_filter_results or {}
        super().__init__(self.message)
