"""Abstract base class for knowledge base search backends."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class KBSearchResult:
    """Result from a knowledge base search operation.

    Attributes:
        content: The formatted search results as a string.
        source: The backend that produced the results (e.g., "azure", "chroma").
        chunk_count: Number of result chunks returned.
        raw_results: Optional list of raw result objects for further processing.
    """

    content: str
    source: str
    chunk_count: int = 0
    raw_results: List[Any] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Check if the search returned no results."""
        return self.chunk_count == 0 or self.content.startswith("No relevant information")


class KBBackend(ABC):
    """Abstract base class for knowledge base search backends.

    This interface defines the contract for all KB search implementations,
    enabling policy-based backend selection and fallback.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the backend name for logging and diagnostics."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int,
        logger: Optional[logging.Logger] = None,
    ) -> KBSearchResult:
        """Execute a search query against the knowledge base.

        Args:
            query: The search query string.
            top_k: Maximum number of results to return.
            logger: Optional logger for diagnostics.

        Returns:
            KBSearchResult containing the search results.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available and properly configured.

        Returns:
            True if the backend can be used, False otherwise.
        """
        pass

    @abstractmethod
    async def validate(self, logger: Optional[logging.Logger] = None) -> None:
        """Validate backend configuration and connectivity.

        Raises:
            PreflightError: If validation fails with specific error details.
        """
        pass

    async def close(self) -> None:
        """Clean up any resources held by the backend.

        Default implementation is a no-op. Override if backend holds resources.
        """
        pass
