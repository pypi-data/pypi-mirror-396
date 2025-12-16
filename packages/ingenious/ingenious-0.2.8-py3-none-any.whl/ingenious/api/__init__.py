"""API module for ingenious FastAPI routes and endpoints.

This module provides extensible path support for API route modules.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
