"""Match data parser utility module.

Provides stub implementation for testing sports/match data parsing with fallback support.
"""

from datetime import datetime
from typing import Any, Optional, Tuple


class MatchDataParser:
    """Stub implementation of MatchDataParser for testing purposes.

    This class handles sports/match data parsing but provides fallback behavior
    for general testing scenarios.

    Attributes:
        payload: The raw payload data to parse.
        event_type: Optional event type identifier.
    """

    def __init__(self, payload: Optional[Any] = None, event_type: Optional[str] = None) -> None:
        """Initialize the match data parser.

        Args:
            payload: The raw payload data to parse.
            event_type: Optional event type identifier.
        """
        self.payload: Optional[Any] = payload
        self.event_type: Optional[str] = event_type

    def create_detailed_summary(self) -> Tuple[str, str, str, str, str]:
        """Create a detailed summary from match data.

        For testing purposes, this returns default values.

        Returns:
            A tuple containing (message, overBall, timestamp, match_id, feed_id).
        """
        # For testing, just return the payload as the message with default values
        message: str = str(self.payload) if self.payload else "test payload"
        overBall: str = "test_over"
        timestamp: str = str(datetime.now())
        match_id: str = "test_match_123"
        feed_id: str = "test_feed_456"

        return message, overBall, timestamp, match_id, feed_id
