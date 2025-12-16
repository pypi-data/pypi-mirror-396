"""Token counting utilities for knowledge base agent.

This module provides defensive token counting that never
fails the main request flow.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple


async def safe_count_tokens(
    system_message: str,
    user_message: str,
    assistant_message: str,
    model: str,
    logger: Optional[logging.Logger] = None,
) -> Tuple[int, int]:
    """Count tokens defensively, never failing the request.

    This function attempts to use tiktoken for accurate counts,
    falling back to character-based estimation if unavailable.

    Args:
        system_message: The system prompt text.
        user_message: The user's input text.
        assistant_message: The assistant's response text.
        model: The model name (for tokenizer selection).
        logger: Optional logger for diagnostics.

    Returns:
        Tuple of (total_tokens, completion_tokens).
    """
    try:
        import tiktoken

        # Try to get encoding for the specific model
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fall back to cl100k_base (GPT-4 encoding)
            encoding = tiktoken.get_encoding("cl100k_base")

        # Count tokens for each part
        system_tokens = len(encoding.encode(system_message)) if system_message else 0
        user_tokens = len(encoding.encode(user_message)) if user_message else 0
        assistant_tokens = len(encoding.encode(assistant_message)) if assistant_message else 0

        # Add overhead for message formatting (approximate)
        # Each message has ~4 tokens overhead for role markers
        overhead = 12  # 3 messages * 4 tokens

        total = system_tokens + user_tokens + assistant_tokens + overhead
        return total, assistant_tokens

    except ImportError:
        if logger:
            logger.debug("tiktoken not available, using character-based estimation")

    except Exception as e:
        if logger:
            logger.debug(f"Token counting failed: {e}")

    # Fallback: character-based estimation
    # Approximate 4 characters per token for English text
    return estimate_tokens_from_chars(system_message, user_message, assistant_message)


def estimate_tokens_from_chars(
    system_message: str,
    user_message: str,
    assistant_message: str,
    chars_per_token: int = 4,
) -> Tuple[int, int]:
    """Estimate token count from character count.

    This is a rough approximation for when tiktoken is unavailable.

    Args:
        system_message: The system prompt text.
        user_message: The user's input text.
        assistant_message: The assistant's response text.
        chars_per_token: Approximate characters per token (default 4).

    Returns:
        Tuple of (estimated_total_tokens, estimated_completion_tokens).
    """
    total_chars = len(system_message or "") + len(user_message or "") + len(assistant_message or "")
    completion_chars = len(assistant_message or "")

    total_tokens = total_chars // chars_per_token
    completion_tokens = completion_chars // chars_per_token

    return total_tokens, completion_tokens


async def finalize_token_counts(
    stream_total: int,
    stream_completion: int,
    system_message: str,
    user_message: str,
    accumulated_content: str,
    model: str,
    logger: Optional[logging.Logger] = None,
) -> Tuple[int, int]:
    """Finalize token counts with fallback logic.

    If stream tokens are 0, recalculate using safe_count_tokens.
    If that also fails, use character-based estimation.

    Args:
        stream_total: Total tokens from streaming (may be 0).
        stream_completion: Completion tokens from streaming (may be 0).
        system_message: The system prompt text.
        user_message: The user's input text.
        accumulated_content: The accumulated response content.
        model: The model name.
        logger: Optional logger for diagnostics.

    Returns:
        Tuple of (total_tokens, completion_tokens).
    """
    if stream_total > 0:
        return stream_total, stream_completion

    # Try accurate counting
    try:
        total, completion = await safe_count_tokens(
            system_message=system_message,
            user_message=user_message,
            assistant_message=accumulated_content,
            model=model,
            logger=logger,
        )
        if total > 0:
            return total, completion
    except Exception:  # nosec B110: intentional fallback to character estimation
        pass

    # Final fallback: character estimation
    return estimate_tokens_from_chars(system_message, user_message, accumulated_content)
