"""Streaming response handling for knowledge base agent.

This module provides utilities for streaming chat responses,
including chunk creation and stream processing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

from ingenious.models.chat import ChatResponseChunk

if TYPE_CHECKING:
    pass


@dataclass
class StreamingState:
    """Mutable state container for streaming response processing.

    Attributes:
        accumulated_content: Content accumulated during streaming.
        total_tokens: Total tokens used (from usage events).
        completion_tokens: Completion tokens used (from usage events).
    """

    accumulated_content: str = ""
    total_tokens: int = 0
    completion_tokens: int = 0


class StreamChunkFactory:
    """Factory for creating ChatResponseChunk objects.

    This class provides convenient methods for creating various
    types of response chunks during streaming.
    """

    @staticmethod
    def status(
        thread_id: str,
        message_id: str,
        content: str,
    ) -> ChatResponseChunk:
        """Create a status chunk.

        Args:
            thread_id: The thread ID.
            message_id: The message ID.
            content: Status message content.

        Returns:
            A status ChatResponseChunk.
        """
        return ChatResponseChunk(
            thread_id=thread_id,
            message_id=message_id,
            chunk_type="status",
            content=content,
            is_final=False,
        )

    @staticmethod
    def content(
        thread_id: str,
        message_id: str,
        content: str,
    ) -> ChatResponseChunk:
        """Create a content chunk.

        Args:
            thread_id: The thread ID.
            message_id: The message ID.
            content: Content text.

        Returns:
            A content ChatResponseChunk.
        """
        return ChatResponseChunk(
            thread_id=thread_id,
            message_id=message_id,
            chunk_type="content",
            content=content,
            is_final=False,
        )

    @staticmethod
    def token_count(
        thread_id: str,
        message_id: str,
        count: int,
    ) -> ChatResponseChunk:
        """Create a token count chunk.

        Args:
            thread_id: The thread ID.
            message_id: The message ID.
            count: Token count value.

        Returns:
            A token_count ChatResponseChunk.
        """
        return ChatResponseChunk(
            thread_id=thread_id,
            message_id=message_id,
            chunk_type="token_count",
            token_count=count,
            is_final=False,
        )

    @staticmethod
    def error(
        thread_id: str,
        message_id: str,
        error_message: str,
    ) -> ChatResponseChunk:
        """Create an error chunk.

        Args:
            thread_id: The thread ID.
            message_id: The message ID.
            error_message: Error description.

        Returns:
            An error ChatResponseChunk.
        """
        return ChatResponseChunk(
            thread_id=thread_id,
            message_id=message_id,
            chunk_type="error",
            content=error_message,
            is_final=True,
        )

    @staticmethod
    def final(
        thread_id: str,
        message_id: str,
        total_tokens: int,
        completion_tokens: int,
        memory_summary: str,
        event_type: str = "knowledge_base_streaming",
    ) -> ChatResponseChunk:
        """Create the final stream chunk.

        Args:
            thread_id: The thread ID.
            message_id: The message ID.
            total_tokens: Total tokens used.
            completion_tokens: Completion tokens used.
            memory_summary: Summary of accumulated content.
            event_type: Event type identifier.

        Returns:
            A final ChatResponseChunk.
        """
        # Truncate memory summary if too long
        if len(memory_summary) > 200:
            memory_summary = memory_summary[:200] + "..."

        return ChatResponseChunk(
            thread_id=thread_id,
            message_id=message_id,
            chunk_type="final",
            token_count=total_tokens,
            max_token_count=completion_tokens,
            memory_summary=memory_summary,
            event_type=event_type,
            is_final=True,
        )


class StreamMessageHandler:
    """Handles processing of streaming messages from LLM agents.

    This class encapsulates the logic for identifying message types
    and extracting content from various AutoGen message formats.
    """

    # Markers indicating tool-related content to filter out
    TOOL_CHATTER_MARKERS = (
        '"tool_calls"',
        '"function":{"name"',
        '"function_call"',
        "Calling tool",
        "Tool result",
        "search_tool(",
    )

    @classmethod
    def is_tool_event(cls, message: Any) -> bool:
        """Check if message is a tool-related event.

        Args:
            message: The message to check.

        Returns:
            True if the message is tool-related.
        """
        return (
            cls._class_name_indicates_tool(message)
            or cls._event_attr_indicates_tool(message)
            or cls._has_tool_attributes(message)
        )

    @classmethod
    def looks_like_tool_chatter(cls, text: str) -> bool:
        """Check if text looks like tool JSON or narration.

        Args:
            text: The text to check.

        Returns:
            True if the text appears to be tool-related noise.
        """
        if not text:
            return False
        return any(marker in text for marker in cls.TOOL_CHATTER_MARKERS)

    @staticmethod
    def _class_name_indicates_tool(obj: Any) -> bool:
        """Check if class name indicates a tool event."""
        cls_name = obj.__class__.__name__.lower()
        return any(k in cls_name for k in ("tool", "functioncall", "function"))

    @staticmethod
    def _event_attr_indicates_tool(obj: Any) -> bool:
        """Check if event attribute indicates a tool event."""
        event = getattr(obj, "event", None)
        return isinstance(event, str) and any(k in event.lower() for k in ("tool", "function"))

    @staticmethod
    def _has_tool_attributes(obj: Any) -> bool:
        """Check if object has tool-related attributes."""
        tool_attrs = ("tool_calls", "function_call", "tool_call_delta")
        for attr in tool_attrs:
            if hasattr(obj, attr):
                return True
            d = getattr(obj, "dict", None)
            if callable(d) and attr in (d() or {}):
                return True
        return False

    @classmethod
    def is_task_result(cls, message: Any) -> bool:
        """Check if message is a TaskResult (final message).

        Args:
            message: The message to check.

        Returns:
            True if the message is a TaskResult.
        """
        return hasattr(message, "__class__") and "TaskResult" in str(message.__class__)

    @classmethod
    def get_task_result_content(cls, message: Any) -> Optional[str]:
        """Extract final content from a TaskResult.

        Args:
            message: The TaskResult message.

        Returns:
            The final content text, or None if not found.
        """
        try:
            final_msgs = getattr(message, "messages", None)
            if final_msgs:
                final_msg = final_msgs[-1]
                return getattr(final_msg, "content", None)
        except Exception:  # nosec B110
            pass
        return None


async def process_agent_stream(
    stream: AsyncIterator[Any],
    thread_id: str,
    message_id: str,
    state: StreamingState,
    logger: Optional[logging.Logger] = None,
) -> AsyncIterator[ChatResponseChunk]:
    """Process an agent stream and yield chat response chunks.

    Args:
        stream: The async iterator from agent.run_stream().
        thread_id: The thread ID for response chunks.
        message_id: The message ID for response chunks.
        state: Mutable state to accumulate content and tokens.
        logger: Optional logger for diagnostics.

    Yields:
        ChatResponseChunk objects for the streaming response.
    """
    factory = StreamChunkFactory()
    handler = StreamMessageHandler()

    try:
        async for message in stream:
            # Handle tool events with status
            if handler.is_tool_event(message):
                yield factory.status(thread_id, message_id, "Searching knowledge base...")
                continue

            # Handle plain text content
            if hasattr(message, "content") and message.content:
                text = str(message.content)
                if not handler.looks_like_tool_chatter(text):
                    state.accumulated_content += text
                    yield factory.content(thread_id, message_id, text)

            # Handle token usage
            if hasattr(message, "usage"):
                usage = message.usage
                if hasattr(usage, "total_tokens"):
                    state.total_tokens = usage.total_tokens
                if hasattr(usage, "completion_tokens"):
                    state.completion_tokens = usage.completion_tokens
                yield factory.token_count(thread_id, message_id, state.total_tokens)

            # Handle TaskResult final flush
            if handler.is_task_result(message):
                final_text = handler.get_task_result_content(message)
                if final_text and final_text not in state.accumulated_content:
                    if not handler.looks_like_tool_chatter(final_text):
                        state.accumulated_content += final_text
                        yield factory.content(thread_id, message_id, final_text)

    except Exception as e:
        if logger:
            logger.error(f"Streaming error: {e}")
        error_text = f"[Error during streaming: {str(e)}]"
        state.accumulated_content += error_text
        yield factory.content(thread_id, message_id, error_text)
