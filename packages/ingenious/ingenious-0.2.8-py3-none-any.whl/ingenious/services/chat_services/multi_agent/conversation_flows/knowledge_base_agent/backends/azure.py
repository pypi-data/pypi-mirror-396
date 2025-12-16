"""Azure AI Search backend implementation."""

from __future__ import annotations

import logging
import os
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, cast

from pydantic import SecretStr

from ingenious.services.retrieval.errors import PreflightError

from .base import KBBackend, KBSearchResult

if TYPE_CHECKING:
    from ingenious.config import IngeniousSettings


class _SearchConfigLike(Protocol):
    """Protocol for search configuration objects."""

    search_index_name: str
    search_endpoint: str
    search_key: SecretStr


class AzureKBBackend(KBBackend):
    """Azure AI Search backend for knowledge base queries.

    This backend integrates with Azure Cognitive Search to provide
    enterprise-grade search capabilities with semantic ranking.
    """

    def __init__(
        self,
        config: "IngeniousSettings",
        snippet_cap: int = 0,
    ) -> None:
        """Initialize the Azure backend.

        Args:
            config: Application configuration containing Azure settings.
            snippet_cap: Optional cap for snippet/content length. 0 means no cap.
        """
        self._config = config
        self._snippet_cap = snippet_cap
        self._provider: Optional[Any] = None

    @property
    def name(self) -> str:
        """Return the backend name."""
        return "Azure AI Search"

    def is_available(self) -> bool:
        """Check if Azure Search is configured and SDK is available.

        Returns:
            True if Azure Search can be used, False otherwise.
        """
        service = self._get_azure_service()
        if not service:
            return False

        endpoint = getattr(service, "endpoint", "") or ""
        key_obj = getattr(service, "key", None) or getattr(service, "api_key", None)
        key_val = self._unwrap_secret(key_obj)

        has_creds = bool(endpoint and key_val and key_val != "mock-search-key-12345")

        if not has_creds:
            return False

        return self._is_sdk_available()

    async def search(
        self,
        query: str,
        top_k: int,
        logger: Optional[logging.Logger] = None,
    ) -> KBSearchResult:
        """Execute a search query against Azure AI Search.

        Args:
            query: The search query string.
            top_k: Maximum number of results to return.
            logger: Optional logger for diagnostics.

        Returns:
            KBSearchResult containing the search results.

        Raises:
            PreflightError: If Azure Search is not available or fails.
        """
        try:
            from ingenious.services.azure_search.provider import AzureSearchProvider

            self._provider = AzureSearchProvider(self._config)
            chunks: List[Dict[str, Any]] = await self._provider.retrieve(query, top_k=top_k)

            if not chunks:
                return KBSearchResult(
                    content=f"No relevant information found in Azure AI Search for query: {query}",
                    source="azure",
                    chunk_count=0,
                )

            formatted = self._format_results(chunks)
            return KBSearchResult(
                content=formatted,
                source="azure",
                chunk_count=len(chunks),
                raw_results=chunks,
            )

        except ImportError as e:
            raise PreflightError(
                provider="azure_search",
                reason="sdk_missing",
                detail=str(e),
            )
        except Exception as e:
            if logger:
                logger.error(f"Azure search failed: {e}")
            raise PreflightError(
                provider="azure_search",
                reason="search_failed",
                detail=str(e),
            )

    async def validate(self, logger: Optional[logging.Logger] = None) -> None:
        """Validate Azure configuration and connectivity.

        Raises:
            PreflightError: If validation fails.
        """
        service = self._get_azure_service()
        if not service:
            raise PreflightError(
                provider="azure_search",
                reason="not_configured",
                detail="Azure Search service missing (azure_search_services[0]).",
            )

        # Ensure index name is set
        self._ensure_default_index(service, logger)

        endpoint = (getattr(service, "endpoint", "") or "").strip()
        index_name = (getattr(service, "index_name", "") or "").strip()
        key_obj = getattr(service, "key", None) or getattr(service, "api_key", None)
        key_val = self._unwrap_secret(key_obj)

        if not endpoint or not key_val or not index_name:
            raise PreflightError(
                provider="azure_search",
                reason="incomplete_config",
                detail=(
                    f"endpoint_present={bool(endpoint)}, key_present={bool(key_val)}, "
                    f"index_name_present={bool(index_name)}"
                ),
            )

        # Perform async network check
        await self._check_connectivity(endpoint, index_name, key_val, logger)

    async def close(self) -> None:
        """Clean up provider resources."""
        if self._provider:
            try:
                await self._provider.close()
            except Exception:  # nosec B110
                pass
            self._provider = None

    def _get_azure_service(self) -> Any:
        """Get the first Azure search service configuration."""
        cfg = getattr(self._config, "azure_search_services", None)
        if not cfg or len(cfg) == 0:
            return None
        return cfg[0]

    def _is_sdk_available(self) -> bool:
        """Check if Azure Search SDK is importable."""
        try:
            from azure.search.documents.aio import SearchClient  # noqa: F401

            return True
        except ImportError:
            return False

    def _unwrap_secret(self, val: Any) -> str:
        """Extract string value from SecretStr or similar."""
        if val is None:
            return ""
        if hasattr(val, "get_secret_value"):
            return str(val.get_secret_value())
        return str(val)

    def _ensure_default_index(self, service: Any, logger: Optional[logging.Logger]) -> None:
        """Ensure an index_name is present, using env default if needed."""
        idx = getattr(service, "index_name", "")
        if idx:
            return

        env_idx = os.getenv("AZURE_SEARCH_DEFAULT_INDEX")
        if env_idx:
            setattr(service, "index_name", env_idx)
            if logger:
                logger.info(
                    "Azure Search 'index_name' not configured; "
                    "using env AZURE_SEARCH_DEFAULT_INDEX=%r.",
                    env_idx,
                )
            return

        default_idx = "test-index"
        setattr(service, "index_name", default_idx)
        if logger:
            logger.warning(
                "Azure Search 'index_name' not configured; using fallback default %r.",
                default_idx,
            )

    async def _check_connectivity(
        self,
        endpoint: str,
        index_name: str,
        key_val: str,
        logger: Optional[logging.Logger],
    ) -> None:
        """Check Azure Search connectivity by getting document count."""
        client = None
        try:
            from ingenious.services.azure_search.client_init import make_async_search_client

            cfg_stub: _SearchConfigLike = SimpleNamespace(
                search_index_name=index_name,
                search_endpoint=endpoint,
                search_key=SecretStr(key_val),
            )
            client = make_async_search_client(cfg_stub)
            await client.get_document_count()

        except ImportError as e:
            raise PreflightError(
                provider="azure_search",
                reason="sdk_missing",
                detail=str(e),
            )
        except Exception as e:
            raise PreflightError(
                provider="azure_search",
                reason="preflight_failed",
                detail=str(e),
            )
        finally:
            if client:
                try:
                    await client.close()
                except Exception:  # nosec B110
                    pass

    def _format_results(self, chunks: List[Dict[str, Any]]) -> str:
        """Format Azure search results into readable string."""
        parts: List[str] = []
        cap = self._snippet_cap

        for i, chunk in enumerate(chunks, 1):
            title = chunk.get("title", chunk.get("id", f"Source {i}"))
            score = chunk.get("_final_score", "")
            snippet = chunk.get("snippet", "") or ""
            content = chunk.get("content", "") or ""

            if cap > 0:
                snippet = cast(str, snippet)[:cap]
                content = cast(str, content)[:cap]

            lines: List[str] = []
            if snippet:
                lines.append(cast(str, snippet))
            if content and content != snippet:
                lines.append(cast(str, content))
            body = "\n".join(lines) if lines else ""

            parts.append(f"[{i}] {title} (score={score})\n{body}")

        return "Found relevant information from Azure AI Search:\n\n" + "\n\n---\n\n".join(parts)
