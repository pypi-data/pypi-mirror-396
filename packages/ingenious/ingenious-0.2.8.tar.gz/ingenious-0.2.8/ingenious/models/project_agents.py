"""Abstract interface for project-specific agent configurations.

This module provides the base interface for defining project-specific
agent configurations that can be implemented by different projects.
"""

from abc import ABC, abstractmethod

from ingenious.config.settings import IngeniousSettings

from .agent_core import Agents


class IProjectAgents(ABC):
    """Abstract base class for project-specific agent configurations.

    This interface defines the contract for retrieving project-specific
    agent configurations. Implementations should provide the agents
    appropriate for their project context.
    """

    def __init__(self) -> None:
        """Initialize the project agents interface."""
        pass

    @abstractmethod
    def Get_Project_Agents(self, config: IngeniousSettings) -> Agents:
        """Get the project-specific agents configuration.

        Args:
            config: The Ingenious settings configuration.

        Returns:
            Agents: The configured Agents collection for the project.
        """
        pass
