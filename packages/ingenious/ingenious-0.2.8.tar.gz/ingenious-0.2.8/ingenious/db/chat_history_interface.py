"""Abstract interface for chat history repository operations.

This module defines the abstract base class for chat history storage operations
across various database backends (SQLite, Azure SQL, Cosmos DB).
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from ingenious.models.message import Message

from .chat_history_models import (
    ChatHistory,
    User,
)

# Re-export types for backward compatibility
__all__ = [
    "IChatHistoryRepository",
    "ChatHistory",
    "User",
]


class IChatHistoryRepository(ABC):
    """Abstract interface for chat history storage operations.

    Defines the contract for storing and retrieving chat history including
    users, threads, messages, steps, elements, and feedback across various
    database backends (SQLite, Azure SQL, Cosmos DB).
    """

    def get_now(self) -> datetime:
        """Get the current UTC datetime.

        Returns:
            Current datetime object in UTC timezone.
        """
        return datetime.now(timezone.utc)

    def get_now_as_string(self) -> str:
        """Get the current UTC datetime as a formatted string.

        Returns:
            ISO-formatted datetime string with microseconds and timezone.
        """
        return self.get_now().strftime("%Y-%m-%d %H:%M:%S.%f%z")

    @abstractmethod
    async def add_message(self, message: Message) -> str:
        """Adds a message to the chat history."""
        pass

    @abstractmethod
    async def add_user(self, identifier: str) -> User:
        """Adds a user to the chat history database."""
        pass

    @abstractmethod
    async def get_user(self, identifier: str) -> User | None:
        """Gets a user from the chat history database."""
        pass

    @abstractmethod
    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        """Gets a message from the chat history."""
        pass

    @abstractmethod
    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        """Retrieve all messages for a specific thread.

        Args:
            thread_id: Unique identifier for the thread.

        Returns:
            List of Message objects belonging to the thread.
        """
        pass

    @abstractmethod
    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        """Update the feedback status for a specific message.

        Args:
            message_id: Unique identifier for the message.
            thread_id: Thread containing the message.
            positive_feedback: True for positive, False for negative, None to clear feedback.
        """
        pass

    @abstractmethod
    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        """Update content filter results for a specific message.

        Args:
            message_id: Unique identifier for the message.
            thread_id: Thread containing the message.
            content_filter_results: Dictionary containing content moderation results.
        """
        pass

    @abstractmethod
    async def delete_thread(self, thread_id: str) -> None:
        """Delete a thread and all associated messages.

        Args:
            thread_id: Unique identifier for the thread to delete.
        """
        pass
