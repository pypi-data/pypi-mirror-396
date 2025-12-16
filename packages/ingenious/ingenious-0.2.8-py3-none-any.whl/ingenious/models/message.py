"""Chat message models for database storage."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    """Chat message model for storing conversation history.

    Attributes:
        user_id: Optional user identifier.
        thread_id: The thread identifier.
        message_id: Optional message identifier.
        positive_feedback: Optional feedback indicator.
        timestamp: Optional message timestamp.
        role: The message role (user, assistant, system, etc.).
        content: The message content text.
        content_filter_results: Optional content filtering results.
        tool_calls: Optional list of tool calls made.
        tool_call_id: Optional tool call identifier.
        tool_call_function: Optional tool call function details.
    """

    user_id: Optional[str]
    thread_id: str
    message_id: Optional[str] = None
    positive_feedback: Optional[bool] = None
    timestamp: Optional[datetime] = None
    role: str
    content: Optional[str] = None
    content_filter_results: Optional[dict[str, object]] = None
    tool_calls: Optional[list[dict[str, object]]] = None
    tool_call_id: Optional[str] = None
    tool_call_function: Optional[dict[str, object]] = None
