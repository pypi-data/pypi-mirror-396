"""Common utilities and shared components.

This module provides extensible path support for common utilities
including enums and shared types.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
