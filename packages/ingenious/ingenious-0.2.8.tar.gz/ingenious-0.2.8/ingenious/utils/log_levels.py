"""Log level constants and conversion utilities.

Provides a centralized definition of logging levels and utilities for converting
between string and integer representations.
"""

from typing import Dict, Optional


class LogLevel:
    """Log level constants and conversion utilities.

    Attributes:
        DEBUG: Debug level (0).
        INFO: Info level (1).
        WARNING: Warning level (2).
        ERROR: Error level (3).
    """

    DEBUG: int = 0
    INFO: int = 1
    WARNING: int = 2
    ERROR: int = 3

    @staticmethod
    def from_string(level_str: str) -> Optional[int]:
        """Convert a string log level to its integer representation.

        Args:
            level_str: The log level as a string (case-insensitive).

        Returns:
            The integer log level, or None if not recognized.
        """
        level_mapping: Dict[str, int] = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
        }
        return level_mapping.get(str(level_str).upper(), None)

    @staticmethod
    def to_string(level: int) -> str:
        """Convert an integer log level to its string representation.

        Args:
            level: The log level as an integer.

        Returns:
            The string log level, or "Unknown" if not recognized.
        """
        level_mapping: Dict[int, str] = {
            LogLevel.DEBUG: "DEBUG",
            LogLevel.INFO: "INFO",
            LogLevel.WARNING: "WARNING",
            LogLevel.ERROR: "ERROR",
        }
        return level_mapping.get(level, "Unknown")
