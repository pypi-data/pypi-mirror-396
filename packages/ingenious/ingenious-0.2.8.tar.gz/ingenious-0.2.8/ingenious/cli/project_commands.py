"""Project management CLI commands for Insight Ingenious.

This module provides backward compatibility while delegating to the new command architecture.
"""

from __future__ import annotations

import typer
from rich.console import Console

from ingenious.cli.commands.project import InitCommand


def register_commands(app: typer.Typer, console: Console) -> None:
    """Register project-related commands with the typer app.

    Args:
        app: Typer application instance to register commands with
        console: Console instance for output formatting
    """

    @app.command(name="init", help="Initialize a new Insight Ingenious project")
    def init() -> None:
        """Initialize a new Insight Ingenious project in the current directory.

        Creates a complete project structure with:
        - .env.example - Example environment variables for pydantic-settings configuration
        - ingenious_extensions/ - Your custom agents and workflows
        - templates/prompts/quickstart-1/ - Ready-to-use bike-insights workflow templates
        - Dockerfile - Docker containerization setup
        - .dockerignore - Docker build exclusions
        - tmp/ - Temporary files and memory storage

        INCLUDES: Pre-configured quickstart-1 templates for immediate bike-insights testing

        NEXT STEPS after running this command:
        1. Copy .env.example to .env and add your credentials
        2. Edit .env file with your API keys and configuration
        3. Validate your configuration: ingen validate
        4. Start the server: ingen serve

        For detailed configuration help: ingen workflows --help
        """
        cmd = InitCommand(console)
        cmd.run()

    # Keep old command for backward compatibility
    @app.command(hidden=True)
    def initialize_new_project() -> None:
        """Generate template folders for a new project (deprecated).

        Creates the following structure:
        - .env.example - Example environment variables for pydantic-settings configuration
        - ingenious_extensions/ - Your custom agents and workflows
        - templates/prompts/quickstart-1/ - Pre-configured bike-insights workflow templates
        - Dockerfile - Docker containerization setup at project root
        - .dockerignore - Docker build exclusions at project root
        - tmp/ - Temporary files and memory

        NEXT STEPS after running this command:
        1. Copy .env.example to .env and fill in your credentials
        2. Edit .env file with your API keys and configuration
        3. Validate your configuration: ingen validate
        4. Start the server: ingen serve

        For workflow-specific configuration requirements, see:
        docs/workflows/README.md
        """
        cmd = InitCommand(console)
        cmd.run()
