"""Azure client factory and builders.

This module provides lazy-loaded Azure service client factories with support
for multiple authentication methods and optional dependencies.
"""

from __future__ import annotations

import importlib
from typing import Any

__all__ = ("AzureClientFactory", "builder")


def __getattr__(name: str) -> Any:
    """Lazy import Azure client factory and builders.

    Args:
        name: Attribute name to import ('AzureClientFactory' or 'builder').

    Returns:
        The requested module or class.

    Raises:
        AttributeError: If the requested attribute is not available.
    """
    # Lazy export of the factory to avoid importing heavy/optional deps at package import time.
    if name == "AzureClientFactory":
        mod = importlib.import_module(".azure_client_builder_factory", __name__)
        return getattr(mod, "AzureClientFactory")
    if name == "builder":
        # Return the builder package module itself; its __init__ is also lightweight/lazy.
        return importlib.import_module(".builder", __name__)
    raise AttributeError(name)
