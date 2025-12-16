"""HTTP error response models."""

from pydantic import BaseModel


class HTTPError(BaseModel):
    """HTTP error response model.

    Attributes:
        detail: The error detail message.
    """

    detail: str
