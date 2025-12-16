"""File storage abstractions and implementations.

This package provides file storage interfaces and implementations for local
and Azure Blob Storage backends, supporting template management and data persistence.

Note:
    This module uses namespace packages to allow extension via plugins.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
