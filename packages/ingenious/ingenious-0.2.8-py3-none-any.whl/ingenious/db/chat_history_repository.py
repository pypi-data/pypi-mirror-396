"""Chat history repository interface and adapters.

Defines the abstract interface for chat history storage and provides adapters
for various backends (SQLite, Azure SQL, Cosmos DB). Includes data models for
users, threads, messages, steps, and elements.

The implementation has been split into:
- chat_history_models: Dataclasses and TypedDicts for data transfer
- chat_history_interface: Abstract base class for repository operations
"""

import importlib
from typing import List, Optional, cast

from ingenious.config import IngeniousSettings
from ingenious.core.structured_logging import get_logger
from ingenious.models.database_client import DatabaseClientType
from ingenious.models.message import Message

# Re-export from split modules for backward compatibility
from .chat_history_interface import IChatHistoryRepository
from .chat_history_models import (
    ChatHistory,
    User,
    get_now,
    get_now_as_string,
)

logger = get_logger(__name__)

# Re-export all for backward compatibility
__all__ = [
    "IChatHistoryRepository",
    "ChatHistoryRepository",
    "ChatHistory",
    "User",
    "get_now",
    "get_now_as_string",
]


class ChatHistoryRepository:
    """Factory-based chat history repository with dynamic backend selection.

    Instantiates the appropriate repository implementation based on database
    type configuration (SQLite, Azure SQL, or Cosmos DB).
    """

    def __init__(self, db_type: DatabaseClientType, config: IngeniousSettings) -> None:
        """Initialize the chat history repository with dynamic database backend.

        Args:
            db_type: Type of database client to use (SQLite, AzureSQL, Cosmos, etc.).
            config: Application configuration settings.

        Raises:
            ValueError: If the specified database client type is not supported.
        """
        module_name = f"ingenious.db.{db_type.value.lower()}"
        class_name = f"{db_type.value.lower()}_ChatHistoryRepository"

        try:
            module = importlib.import_module(module_name)
            repository_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported database client type: {module_name}.{class_name}") from e

        self.repository = repository_class(config=config)

    async def add_user(self, identifier: str) -> User:
        """Add a new user to the chat history database.

        Args:
            identifier: Unique user identifier string.

        Returns:
            User object containing the created user information.
        """
        return cast(User, await self.repository.add_user(identifier))

    async def get_user(self, identifier: str) -> User | None:
        """Retrieve a user by their identifier.

        Args:
            identifier: Unique user identifier string.

        Returns:
            User object if found, None otherwise.
        """
        return cast(User | None, await self.repository.get_user(identifier))

    async def add_message(self, message: Message) -> str:
        """Add a message to the chat history.

        Args:
            message: Message object containing role, content, and metadata.

        Returns:
            Message ID as a string after successful creation.
        """
        return str(await self.repository.add_message(message))

    async def add_memory(self, memory: Message) -> str:
        """Add a memory entry to the chat history.

        Args:
            memory: Message object representing a memory to store.

        Returns:
            Memory ID as a string after successful creation.
        """
        return str(await self.repository.add_memory(memory))

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        """Retrieve a specific message by ID and thread.

        Args:
            message_id: Unique identifier for the message.
            thread_id: Thread containing the message.

        Returns:
            Message object if found, None otherwise.
        """
        return cast(Message | None, await self.repository.get_message(message_id, thread_id))

    async def get_memory(self, message_id: str, thread_id: str) -> Message | None:
        """Retrieve a specific memory entry by ID and thread.

        Args:
            message_id: Unique identifier for the memory entry.
            thread_id: Thread containing the memory.

        Returns:
            Message object representing the memory if found, None otherwise.
        """
        return cast(Message | None, await self.repository.get_memory(message_id, thread_id))

    async def update_memory(self) -> None:
        """Update memory entries in the chat history.

        This method performs batch updates or maintenance on memory entries.
        """
        await self.repository.update_memory()
        return None

    async def get_thread_messages(self, thread_id: str) -> Optional[List[Message]]:
        """Retrieve all messages for a specific thread.

        Args:
            thread_id: Unique identifier for the thread.

        Returns:
            List of Message objects belonging to the thread, or None if thread not found.
        """
        return cast(
            Optional[List[Message]],
            await self.repository.get_thread_messages(thread_id),
        )

    async def get_thread_memory(self, thread_id: str) -> Optional[List[Message]]:
        """Retrieve all memory entries for a specific thread.

        Args:
            thread_id: Unique identifier for the thread.

        Returns:
            List of Message objects representing memories for the thread, or None if thread not found.
        """
        return cast(Optional[List[Message]], await self.repository.get_thread_memory(thread_id))

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        """Update the feedback status for a specific message.

        Args:
            message_id: Unique identifier for the message.
            thread_id: Thread containing the message.
            positive_feedback: True for positive, False for negative, None to clear feedback.
        """
        await self.repository.update_message_feedback(message_id, thread_id, positive_feedback)
        return None

    async def update_memory_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        """Update the feedback status for a specific memory entry.

        Args:
            message_id: Unique identifier for the memory entry.
            thread_id: Thread containing the memory.
            positive_feedback: True for positive, False for negative, None to clear feedback.
        """
        await self.repository.update_memory_feedback(message_id, thread_id, positive_feedback)
        return None

    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        """Update content filter results for a specific message.

        Args:
            message_id: Unique identifier for the message.
            thread_id: Thread containing the message.
            content_filter_results: Dictionary containing content moderation results.
        """
        await self.repository.update_message_content_filter_results(
            message_id, thread_id, content_filter_results
        )
        return None

    async def update_memory_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        """Update content filter results for a specific memory entry.

        Args:
            message_id: Unique identifier for the memory entry.
            thread_id: Thread containing the memory.
            content_filter_results: Dictionary containing content moderation results.
        """
        await self.repository.update_memory_content_filter_results(
            message_id, thread_id, content_filter_results
        )
        return None

    async def delete_thread(self, thread_id: str) -> None:
        """Delete a thread and all associated messages.

        Args:
            thread_id: Unique identifier for the thread to delete.
        """
        await self.repository.delete_thread(thread_id)
        return None

    async def delete_thread_memory(self, thread_id: str) -> None:
        """Delete all memory entries for a specific thread.

        Args:
            thread_id: Unique identifier for the thread whose memory to delete.
        """
        await self.repository.delete_thread_memory(thread_id)
        return None

    async def delete_user_memory(self, user_id: str) -> None:
        """Delete all memory entries for a specific user.

        Args:
            user_id: Unique identifier for the user whose memory to delete.
        """
        await self.repository.delete_user_memory(user_id)
