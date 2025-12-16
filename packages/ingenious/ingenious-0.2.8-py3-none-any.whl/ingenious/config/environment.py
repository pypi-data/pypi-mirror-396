"""Environment variable handling and configuration loading.

This module handles environment variable processing and
provides utilities for loading configuration from different sources.
"""

import os
from typing import TYPE_CHECKING

from pydantic_settings import SettingsConfigDict

if TYPE_CHECKING:
    from .main_settings import IngeniousSettings


def get_settings_config() -> SettingsConfigDict:
    """Get the standard settings configuration for pydantic-settings.

    Returns:
        Configuration dictionary for pydantic-settings with INGENIOUS_ prefix,
        nested delimiter, and .env file support.
    """
    return SettingsConfigDict(
        env_prefix="INGENIOUS_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )


def load_from_env_file(env_file: str = ".env") -> "IngeniousSettings":
    """Load settings from a specific .env file.

    Args:
        env_file: Path to the environment file to load.

    Returns:
        Loaded and validated IngeniousSettings instance.
    """
    from .main_settings import IngeniousSettings

    return IngeniousSettings(_env_file=env_file)


def create_minimal_config() -> "IngeniousSettings":
    """Create a minimal configuration for development.

    Returns:
        IngeniousSettings instance configured with minimal defaults suitable
        for local development and testing.

    Note:
        This function requires INGENIOUS_MODELS__0__API_KEY and
        INGENIOUS_MODELS__0__BASE_URL environment variables to be set.
    """
    from .main_settings import IngeniousSettings
    from .models import (
        LoggingSettings,
        ModelSettings,
        WebAuthenticationSettings,
        WebSettings,
    )

    api_key = os.getenv("INGENIOUS_MODELS__0__API_KEY", "")
    base_url = os.getenv("INGENIOUS_MODELS__0__BASE_URL", "")
    model_name = os.getenv("INGENIOUS_MODELS__0__MODEL", "gpt-4o-mini")
    deployment = os.getenv("INGENIOUS_MODELS__0__DEPLOYMENT", model_name)

    if not api_key or not base_url:
        raise ValueError(
            "Minimal config requires INGENIOUS_MODELS__0__API_KEY and "
            "INGENIOUS_MODELS__0__BASE_URL environment variables."
        )

    return IngeniousSettings(
        models=[
            ModelSettings(
                model=model_name,
                api_type="rest",
                api_version="2024-12-01-preview",
                api_key=api_key,
                base_url=base_url,
                deployment=deployment,
            )
        ],
        logging=LoggingSettings(root_log_level="debug", log_level="debug"),
        web_configuration=WebSettings(
            ip_address="0.0.0.0",  # nosec B104: intentional for container deployments
            port=8000,
            type="fastapi",
            asynchronous=False,
            authentication=WebAuthenticationSettings(  # nosec B106: dev config, auth disabled
                enable=False, username="admin", password="", type="basic"
            ),
        ),
    )
