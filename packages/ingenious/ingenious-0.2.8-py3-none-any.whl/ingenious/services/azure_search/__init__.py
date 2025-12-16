"""Azure AI Search service module.

This module provides the main interface for Azure AI Search integration with
the ingenious framework. It exports key components and factories for building
search pipelines with lazy SDK loading.
"""

from typing import TYPE_CHECKING, Any

from ingenious.services.retrieval.errors import GenerationDisabledError  # noqa: F401

# Export the light model directly – safe to import anytime
from .config import SearchConfig  # noqa: F401


def build_search_pipeline(*args: Any, **kwargs: Any) -> "AdvancedSearchPipeline":
    """Build a search pipeline with lazy Azure SDK imports.

    This function acts as a lazy proxy to delay importing Azure SDKs until
    the pipeline is actually constructed and called.

    Args:
        *args: Positional arguments forwarded to the pipeline factory.
        **kwargs: Keyword arguments forwarded to the pipeline factory.

    Returns:
        An initialized AdvancedSearchPipeline instance.
    """
    from .components.pipeline import build_search_pipeline as _impl

    return _impl(*args, **kwargs)


if TYPE_CHECKING:
    # Only for type checkers; doesn't run at runtime
    from .components.pipeline import AdvancedSearchPipeline  # noqa: F401

__all__ = [
    "SearchConfig",
    "build_search_pipeline",
    "AdvancedSearchPipeline",
    "GenerationDisabledError",
]
