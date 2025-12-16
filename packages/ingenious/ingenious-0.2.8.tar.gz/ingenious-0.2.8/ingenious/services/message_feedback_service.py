"""Message feedback service for handling user feedback on chat messages.

This module provides functionality for updating and managing user feedback
on chat messages in the conversation history.
"""

from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)


class MessageFeedbackService:
    """Handle message feedback operations.

    Attributes:
        chat_history_repository: Repository for accessing chat history and messages.
    """

    def __init__(self, chat_history_repository: ChatHistoryRepository):
        """Initialize message feedback service.

        Args:
            chat_history_repository: Repository for accessing chat history data.
        """
        self.chat_history_repository = chat_history_repository

    async def update_message_feedback(
        self, message_id: str, message_feedback_request: MessageFeedbackRequest
    ) -> MessageFeedbackResponse:
        """Update feedback for a specific message.

        Args:
            message_id: ID of the message to update feedback for.
            message_feedback_request: Feedback request containing user feedback data.

        Returns:
            Response confirming feedback submission.

        Raises:
            ValueError: If message_id doesn't match request, message not found, or user_id mismatch.
        """
        # Validate message ID
        if message_id != message_feedback_request.message_id:
            raise ValueError("Message ID does not match message feedback request.")

        # Get message from DB
        message = await self.chat_history_repository.get_message(
            message_id, message_feedback_request.thread_id
        )
        if not message:
            raise ValueError(f"Message {message_id} not found.")

        # Validate user ID
        if (message.user_id or "") != (message_feedback_request.user_id or ""):
            raise ValueError("User ID does not match message feedback request.")

        # Update feedback
        await self.chat_history_repository.update_message_feedback(
            message_id,
            message_feedback_request.thread_id,
            message_feedback_request.positive_feedback,
        )

        return MessageFeedbackResponse(message=f"Feedback submitted for message {message_id}.")
