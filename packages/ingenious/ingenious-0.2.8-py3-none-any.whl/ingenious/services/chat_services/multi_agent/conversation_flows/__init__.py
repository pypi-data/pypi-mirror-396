"""Conversation flows for multi-agent chat service.

This module contains conversation flow implementations that follow the
IConversationFlow interface and can be dynamically discovered and used
by the multi-agent chat service.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
