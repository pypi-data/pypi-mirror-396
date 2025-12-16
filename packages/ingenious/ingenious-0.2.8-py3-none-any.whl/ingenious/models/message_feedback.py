"""Message feedback request and response models."""

from typing import Optional

from pydantic import BaseModel


class MessageFeedbackRequest(BaseModel):
    """Request model for submitting message feedback.

    Attributes:
        thread_id: The thread identifier.
        message_id: The message identifier.
        user_id: Optional user identifier.
        positive_feedback: Optional boolean indicating positive feedback.
    """

    thread_id: str
    message_id: str
    user_id: Optional[str] = None
    positive_feedback: Optional[bool] = None


class MessageFeedbackResponse(BaseModel):
    """Response model for message feedback submission.

    Attributes:
        message: Response message confirming feedback submission.
    """

    message: str
