"""Legacy configuration utilities."""

from ingenious.config import IngeniousSettings
from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)


def get_config(project_path: str = "") -> IngeniousSettings:
    """Get configuration using pydantic-settings system.

    This function provides configuration management that:
    - Automatically loads environment variables
    - Supports .env files
    - Provides validation with helpful error messages
    - Uses nested configuration models

    Args:
        project_path: Optional project path (for backward compatibility)

    Returns:
        IngeniousSettings: The loaded and validated configuration
    """
    try:
        settings = IngeniousSettings()
        settings.validate_configuration()
        return settings
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise
