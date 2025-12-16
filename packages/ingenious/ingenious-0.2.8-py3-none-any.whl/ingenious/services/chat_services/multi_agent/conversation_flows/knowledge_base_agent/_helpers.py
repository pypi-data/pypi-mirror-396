"""Internal helper utilities for knowledge base conversation flow.

This module contains stateless utility functions extracted from knowledge_base_agent.py
for better organization and testability. These are internal implementation details and
should not be imported directly by external code.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, List, Optional, Tuple

# Try YAML; fall back to JSON/plaintext if PyYAML isn't installed
try:
    import yaml
except Exception:
    yaml = None  # sentinel to denote "no YAML available"


# -----------------------------------------------------------------------------
# Text conversion utilities
# -----------------------------------------------------------------------------


def as_text(x: Any) -> str:
    """Safely coerce any object (list/dict/bytes/etc.) to text.

    This function provides a robust fallback for converting arbitrary data to a
    string. It handles None, bytes, and attempts to serialize other types as
    JSON before resorting to the standard `str()` representation, preventing
    conversion errors from propagating.

    Args:
        x: The object to convert.

    Returns:
        A string representation of the input.
    """
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, bytes):
        try:
            return x.decode("utf-8", "replace")
        except Exception:
            return str(x)
    try:
        return json.dumps(x, ensure_ascii=False)
    except Exception:
        return str(x)


def to_text(x: Any) -> str:
    """Prefer joining lists of strings; otherwise fall back to JSON/str via as_text.

    This function is designed to provide a more natural string representation for
    lists by joining their elements. For all non-list types, it delegates the
    conversion to the `as_text` function for safe, generic handling.

    Args:
        x: The object to convert.

    Returns:
        A string representation of the input, with special handling for lists.
    """
    if isinstance(x, list):
        parts: list[str] = []
        for p in x:
            parts.append(p if isinstance(p, str) else as_text(p))
        return "".join(parts)
    return as_text(x)


def diagnostics_enabled() -> bool:
    """Global opt-in switch for diagnostics that may expose configuration (never full secrets)."""
    v = os.getenv("INGENIOUS_DIAGNOSTICS_ENABLED", "")
    return v.strip().lower() in {"1", "true", "yes", "on"}


# -----------------------------------------------------------------------------
# Secret/credential utilities
# -----------------------------------------------------------------------------


def unwrap_secret_or_str(val: Any) -> str:
    """Return the raw secret value if `val` is a secret object; else str(val)."""
    if hasattr(val, "get_secret_value"):
        try:
            return val.get_secret_value()
        except Exception:
            return ""
    return str(val) if val is not None else ""


def mask_secret(s: str | None) -> str:
    """Mask a secret: short -> 'a***d'; long -> 'abcd...wxyz (len=NN)'."""
    s = s or ""
    if len(s) <= 8:
        return (s[:1] + "***" + s[-1:]) if s else "<empty>"
    return f"{s[:4]}...{s[-4:]} (len={len(s)})"


# -----------------------------------------------------------------------------
# Azure availability check
# -----------------------------------------------------------------------------


def is_azure_search_available() -> bool:
    """Best-effort check that the Azure Search provider/SDK is importable.

    Does not validate network/keys; runtime failures still fall back (if policy allows).
    """
    try:
        from ingenious.services.azure_search.provider import (
            AzureSearchProvider,
        )

        _ = AzureSearchProvider  # silence linter
        return True
    except Exception:
        return False


# -----------------------------------------------------------------------------
# Token counting
# -----------------------------------------------------------------------------


async def safe_count_tokens(
    system_message: str,
    user_message: str,
    assistant_message: str,
    model: str,
    logger: Optional[logging.Logger] = None,
) -> Tuple[int, int]:
    """Compute token counts defensively; never fail the request."""
    try:
        from ingenious.utils.token_counter import num_tokens_from_messages

        msgs: list[dict[str, Any]] = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ]
        total = num_tokens_from_messages(msgs, model)
        prompt = num_tokens_from_messages(msgs[:-1], model)
        completion = total - prompt
        return total, completion
    except Exception as e:
        if logger:
            logger.warning(f"Token counting failed: {e}")
        return 0, 0


# -----------------------------------------------------------------------------
# System prompt builders
# -----------------------------------------------------------------------------


def static_system_message(memory_context: str) -> str:
    """Deterministic system prompt for direct mode."""
    prefix = (
        "You are a knowledge base search assistant that uses Azure AI Search or local ChromaDB.\n\n"
    )
    if memory_context:
        prefix += memory_context
    prefix += (
        "Always base your responses on knowledge base search results. "
        "If nothing is found, clearly state that and suggest rephrasing the query. "
        "TERMINATE your response when the task is complete."
    )
    return prefix


def assist_system_message(memory_context: str) -> str:
    """Richer prompt for assist mode (summarization + guidelines + citation hint)."""
    parts = [
        "You are a knowledge base search assistant that can use both Azure AI Search and local ChromaDB storage.\n",
    ]
    if memory_context:
        parts.append(memory_context)

    parts.append(
        "IMPORTANT: If there is previous conversation context above, you MUST:\n"
        "- Reference it when answering follow-up questions\n"
        "- Use information from previous searches to inform new searches\n"
        "- Maintain context about what information has already been discussed\n"
        '- Answer questions that refer to "it", "that", "those" etc. based on previous context\n\n'
        "Tasks:\n"
        "- Help users find information by searching the knowledge base\n"
        "- Use the search_tool to look up information\n"
        "- Always base your responses on search results from the knowledge base\n"
        "- Always consider and reference previous conversation when relevant\n"
        "- If no information is found, clearly state that and suggest rephrasing the query\n\n"
        "Guidelines for search queries:\n"
        "- Use specific, relevant keywords\n"
        "- Try different phrasings if initial search doesn't return results\n"
        "- Focus on topics that are relevant to the knowledge base content\n\n"
        "Format your responses clearly and cite the knowledge base when providing information.\n"
        "TERMINATE your response when the task is complete."
    )
    return "".join(parts)


def streaming_system_message(memory_context: str) -> str:
    """Streaming prompt with guidance, topics, and citation directive."""
    parts: List[str] = [
        "You are a knowledge base search assistant that can use both Azure AI Search and local ChromaDB storage.\n\n"
    ]
    if memory_context:
        parts.append(memory_context)

    parts.append(
        "IMPORTANT: Maintain context and base your responses on search results.\n\n"
        "Guidelines for search queries:\n"
        "- Use specific, relevant keywords\n"
        "- Try different phrasings if initial search doesn't return results\n"
        "- Focus on topics that are relevant to the knowledge base content\n\n"
        "Knowledge base contains documents about:\n"
        "- Azure configuration and setup\n"
        "- Workplace safety guidelines\n"
        "- Health information and nutrition\n"
        "- Emergency procedures\n"
        "- Mental health and wellbeing\n"
        "- First aid basics\n"
        "- General informational content\n\n"
        "Format your responses clearly and cite the knowledge base when providing information."
    )
    return "".join(parts)
