"""Chat services package for various chat service implementations.

This package uses namespace package functionality to support extensible
chat service implementations. It allows combining modules from multiple
locations into a single namespace.

Note:
    This extends the package path to include all subdirectories named
    'chat_services' on sys.path, enabling plugin-style architecture.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
