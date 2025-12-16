"""Configuration validation logic.

This module contains validation functions for ensuring configuration integrity.
All configuration must be provided via INGENIOUS_* environment variables.
"""

from typing import TYPE_CHECKING, List

from ingenious.common.enums import AuthenticationMethod

from .models import ModelSettings

if TYPE_CHECKING:
    from .main_settings import IngeniousSettings


def _validate_single_model(model: ModelSettings, index: int) -> List[str]:
    """Validate a single model's configuration and return any errors."""
    errors: List[str] = []
    requires_api_key = model.authentication_method == AuthenticationMethod.TOKEN

    if requires_api_key:
        if not model.api_key:
            errors.append(
                f"Model {index + 1} has no API key (required for TOKEN "
                f"authentication). Set INGENIOUS_MODELS__{index}__API_KEY."
            )
        elif "placeholder" in model.api_key.lower():
            errors.append(
                f"Model {index + 1} has placeholder API key. "
                "Set a valid API key in environment variables."
            )

    if not model.base_url:
        errors.append(
            f"Model {index + 1} has no base URL. Set INGENIOUS_MODELS__{index}__BASE_URL."
        )
    elif "placeholder" in model.base_url.lower():
        errors.append(
            f"Model {index + 1} has placeholder base URL. "
            "Set a valid base URL in environment variables."
        )

    # Validate base_url is a valid URL format
    if model.base_url and not model.base_url.startswith(("http://", "https://")):
        errors.append(
            f"Model {index + 1} base URL must start with http:// or https://. Got: {model.base_url}"
        )

    return errors


def _strip_string_fields(model: ModelSettings) -> None:
    """Strip whitespace from string fields in model configuration."""
    if model.api_key:
        model.api_key = model.api_key.strip()
    if model.base_url:
        model.base_url = model.base_url.strip()
    if model.model:
        model.model = model.model.strip()
    if model.deployment:
        model.deployment = model.deployment.strip()


def validate_configuration(settings: "IngeniousSettings") -> None:
    """Validate the complete configuration and provide helpful feedback.

    This function performs comprehensive validation of all configuration
    settings and provides clear, actionable error messages.
    """
    errors: List[str] = []

    if not settings.models:
        errors.append(
            "No models configured. Set INGENIOUS_MODELS__0__API_KEY and "
            "INGENIOUS_MODELS__0__BASE_URL."
        )

    for i, model in enumerate(settings.models):
        # Strip whitespace from string fields
        _strip_string_fields(model)
        # Validate model configuration
        errors.extend(_validate_single_model(model, i))

    if (
        settings.web_configuration.authentication.enable
        and not settings.web_configuration.authentication.password
    ):
        errors.append(
            "Web authentication is enabled but no password is set. "
            "Set INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__PASSWORD."
        )

    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(
            f"- {error}" for error in errors
        )
        error_msg += "\n\nSee documentation for configuration examples."
        raise ValueError(error_msg)
