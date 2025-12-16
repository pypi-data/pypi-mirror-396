"""Interface for custom API route handlers."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI

from ingenious.core.structured_logging import get_logger

if TYPE_CHECKING:
    from ingenious.config.settings import IngeniousSettings


class IApiRoutes(ABC):
    """Interface for adding custom API routes to FastAPI applications.

    Attributes:
        config: The IngeniousSettings configuration instance.
        logger: The structured logger instance.
        app: The FastAPI application instance.
    """

    def __init__(self, config: "IngeniousSettings", app: FastAPI):
        """Initialize the API routes handler.

        Args:
            config: The IngeniousSettings configuration instance.
            app: The FastAPI application instance.
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.app = app
        # Note: repositories and services should be obtained via dependency injection in route handlers

    @abstractmethod
    def add_custom_routes(self) -> APIRouter:
        """Adds custom routes to the FastAPI app instance.

        Returns:
            The router instance with custom routes added.
        """
        pass
