"""Token limit exceeded error exception.

This module defines exceptions raised when token limits are exceeded during chat operations.
"""


class TokenLimitExceededError(Exception):
    """Exception raised when user has exceeded OpenAI token limit.

    Attributes:
        DEFAULT_MESSAGE (str): Default error message for token limit exceeded.
        message (str): Error message describing the limit exceeded.
        max_context_length (int): Maximum allowed context length.
        requested_tokens (int): Number of tokens requested.
        prompt_tokens (int): Number of tokens in prompt.
        completion_tokens (int): Number of tokens in completion.
    """

    DEFAULT_MESSAGE = "This chat has exceeded the token limit, please start a new conversation."

    def __init__(
        self,
        message: str = DEFAULT_MESSAGE,
        max_context_length: int = 0,
        requested_tokens: int = 0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> None:
        """Initialize token limit exceeded error.

        Args:
            message (str): Error message, defaults to DEFAULT_MESSAGE.
            max_context_length (int): Maximum allowed context length.
            requested_tokens (int): Number of tokens requested.
            prompt_tokens (int): Number of tokens in prompt.
            completion_tokens (int): Number of tokens in completion.
        """
        self.message = message
        self.max_context_length = max_context_length
        self.requested_tokens = requested_tokens
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        super().__init__(self.message)
