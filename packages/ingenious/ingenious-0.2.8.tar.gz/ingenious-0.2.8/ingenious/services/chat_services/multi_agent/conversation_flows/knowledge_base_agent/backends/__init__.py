"""Knowledge base search backends.

This package provides modular backend implementations for knowledge base search,
supporting both Azure AI Search and local ChromaDB.
"""

from .azure import AzureKBBackend
from .base import KBBackend, KBSearchResult
from .chroma import ChromaKBBackend

__all__ = [
    "KBBackend",
    "KBSearchResult",
    "AzureKBBackend",
    "ChromaKBBackend",
]
