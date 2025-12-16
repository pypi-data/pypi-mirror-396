"""External service integrations for Ingenious.

This package provides integrations with external services including OpenAI
and Azure services, with support for various authentication methods.

Note:
    This module uses namespace packages to allow extension via plugins.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
