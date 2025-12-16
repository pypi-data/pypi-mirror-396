"""Local ChromaDB backend implementation."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, List, Optional, Tuple

from .base import KBBackend, KBSearchResult


class ChromaKBBackend(KBBackend):
    """Local ChromaDB backend for knowledge base queries.

    This backend uses ChromaDB for local vector search, supporting
    offline operation and development scenarios without Azure dependencies.
    """

    def __init__(
        self,
        kb_path: str,
        chroma_persist_path: str,
        collection_name: str = "knowledge_base",
    ) -> None:
        """Initialize the ChromaDB backend.

        Args:
            kb_path: Path to the knowledge base directory containing documents.
            chroma_persist_path: Path where ChromaDB should persist its data.
            collection_name: Name of the ChromaDB collection to use.
        """
        self._kb_path = kb_path
        self._chroma_path = chroma_persist_path
        self._collection_name = collection_name
        self._client: Optional[Any] = None
        self._collection: Optional[Any] = None

    @property
    def name(self) -> str:
        """Return the backend name."""
        return "ChromaDB"

    def is_available(self) -> bool:
        """Check if ChromaDB is installed and KB directory exists.

        Returns:
            True if ChromaDB can be used, False otherwise.
        """
        try:
            import chromadb  # noqa: F401

            return os.path.exists(self._kb_path)
        except ImportError:
            return False

    async def search(
        self,
        query: str,
        top_k: int,
        logger: Optional[logging.Logger] = None,
    ) -> KBSearchResult:
        """Execute a search query against ChromaDB.

        Args:
            query: The search query string.
            top_k: Maximum number of results to return.
            logger: Optional logger for diagnostics.

        Returns:
            KBSearchResult containing the search results.
        """
        # Check KB directory
        dir_error = self._check_kb_directory(logger)
        if dir_error:
            return KBSearchResult(
                content=dir_error,
                source="chroma",
                chunk_count=0,
            )

        # Import ChromaDB
        try:
            import chromadb
        except ImportError:
            return KBSearchResult(
                content="Error: ChromaDB not installed. Please install with: uv add chromadb",
                source="chroma",
                chunk_count=0,
            )

        # Initialize client and collection
        if self._client is None:
            self._client = chromadb.PersistentClient(path=self._chroma_path)

        collection, create_error = await self._get_or_create_collection(logger)
        if create_error:
            return KBSearchResult(
                content=create_error,
                source="chroma",
                chunk_count=0,
            )

        # Execute search
        try:
            results = collection.query(query_texts=[query], n_results=top_k)
        except Exception as e:
            if logger:
                logger.error(f"ChromaDB query failed: {e}")
            return KBSearchResult(
                content=f"Search error: {str(e)}",
                source="chroma",
                chunk_count=0,
            )

        # Format results
        docs = results.get("documents") or []
        if docs and docs[0]:
            content = "Found relevant information from ChromaDB:\n\n" + "\n\n".join(docs[0])
            return KBSearchResult(
                content=content,
                source="chroma",
                chunk_count=len(docs[0]),
                raw_results=docs[0],
            )

        return KBSearchResult(
            content=f"No relevant information found in ChromaDB for query: {query}",
            source="chroma",
            chunk_count=0,
        )

    async def validate(self, logger: Optional[logging.Logger] = None) -> None:
        """Validate ChromaDB configuration.

        Raises:
            ValueError: If ChromaDB is not available or KB directory missing.
        """
        try:
            import chromadb  # noqa: F401
        except ImportError:
            raise ValueError("ChromaDB not installed. Install with: uv add chromadb")

        if not os.path.exists(self._kb_path):
            raise ValueError(f"Knowledge base directory not found: {self._kb_path}")

    async def close(self) -> None:
        """Clean up ChromaDB resources."""
        self._collection = None
        self._client = None

    def _check_kb_directory(self, logger: Optional[logging.Logger]) -> Optional[str]:
        """Check if KB directory exists and contains documents.

        Returns:
            Error message if directory is missing, None otherwise.
        """
        if os.path.exists(self._kb_path):
            return None

        if logger:
            logger.warning("Knowledge base directory missing: %s", self._kb_path)

        kb_display = self._kb_path
        if not kb_display.endswith(os.sep):
            kb_display = kb_display + os.sep

        return f"Error: Knowledge base directory is empty. Please add documents to {kb_display}"

    async def _get_or_create_collection(
        self, logger: Optional[logging.Logger]
    ) -> Tuple[Any, Optional[str]]:
        """Get or create the ChromaDB collection.

        Returns:
            Tuple of (collection, error_message). error_message is None on success.
        """
        if self._collection is not None:
            return self._collection, None

        # _client is initialized before this method is called
        if self._client is None:
            return None, "Error: ChromaDB client not initialized"

        try:
            self._collection = self._client.get_collection(name=self._collection_name)
            return self._collection, None
        except Exception:
            # Collection doesn't exist, create it
            self._collection = self._client.create_collection(name=self._collection_name)

            # Load documents
            docs, ids = await self._read_documents()
            if not docs:
                return self._collection, "Error: No documents found in knowledge base directory"

            try:
                self._collection.add(documents=docs, ids=ids)
            except Exception as e:
                if logger:
                    logger.warning(f"ChromaDB add() failed: {e}")

            return self._collection, None

    async def _read_documents(self) -> Tuple[List[str], List[str]]:
        """Read documents from the knowledge base directory.

        Returns:
            Tuple of (documents, ids) lists.
        """

        def _read() -> Tuple[List[str], List[str]]:
            """Blocking read operation run in thread pool."""
            documents: List[str] = []
            ids: List[str] = []

            if not os.path.exists(self._kb_path):
                return documents, ids

            for filename in os.listdir(self._kb_path):
                if filename.endswith((".md", ".txt")):
                    filepath = os.path.join(self._kb_path, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                    except Exception:  # nosec B112
                        continue

                    # Simple blank-line chunking
                    chunks = content.split("\n\n")
                    for i, chunk in enumerate(chunks):
                        chunk = chunk.strip()
                        if chunk:
                            documents.append(chunk)
                            ids.append(f"{filename}_chunk_{i}")

            return documents, ids

        return await asyncio.to_thread(_read)

    def ensure_directory(self) -> None:
        """Ensure the KB directory exists."""
        try:
            os.makedirs(self._kb_path, exist_ok=True)
        except Exception:  # nosec B110
            pass
