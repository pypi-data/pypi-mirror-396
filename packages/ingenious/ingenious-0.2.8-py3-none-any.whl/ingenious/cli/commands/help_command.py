"""Help CLI command for Insight Ingenious.

This module contains the help command for getting started guidance.
"""

from __future__ import annotations

from typing import Any, Optional

from rich.panel import Panel

from ingenious.cli.base import BaseCommand, CommandError, ExitCode


class HelpCommand(BaseCommand):
    """Show detailed help and getting started guide."""

    def execute(self, topic: Optional[str] = None, **kwargs: Any) -> None:
        """Show comprehensive help for getting started with Insight Ingenious.

        Args:
            topic: Specific topic to show help for (setup, workflows, config, deployment)
            **kwargs: Additional keyword arguments (unused)
        """
        if topic is None:
            self._show_general_help()
        elif topic == "setup":
            self._show_setup_help()
        elif topic == "workflows":
            self._show_workflows_help()
        elif topic == "config":
            self._show_config_help()
        elif topic == "deployment":
            self._show_deployment_help()
        else:
            self.print_error(f"Unknown help topic: {topic}")
            self.console.print("\nAvailable topics: setup, workflows, config, deployment")
            self.console.print("Use 'ingen help' for general help.")
            raise CommandError(f"Invalid help topic: {topic}", ExitCode.VALIDATION_ERROR)

    def _show_general_help(self) -> None:
        """Show general help information."""
        self.console.print("[bold blue]🚀 Insight Ingenious - Quick Start Guide[/bold blue]\n")

        sections = [
            ("1. Initialize a new project:", "ingen init"),
            (
                "2. Configure your project:",
                "• Copy .env.example to .env and add your API keys\n   • Update config.yml and profiles.yml as needed",
            ),
            (
                "3. Set environment variables:",
                "export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml\n   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml",
            ),
            ("4. Start the server:", "ingen serve"),
            (
                "5. Access the interfaces:",
                "• API: http://localhost:80\n   • Chat: http://localhost:80/chainlit\n   • Prompt Tuner: http://localhost:80/prompt-tuner",
            ),
        ]

        for title, content in sections:
            self.console.print(f"[bold]{title}[/bold]")
            self.console.print(f"   {content}")
            self.console.print("")

        helpful_commands = Panel(
            "ingen status      # Check configuration\n"
            "ingen workflows   # List available workflows\n"
            "ingen test        # Run tests\n"
            "ingen help <topic> # Get detailed help on specific topics",
            title="💡 Helpful Commands",
            border_style="yellow",
        )
        self.console.print(helpful_commands)

        docs_panel = Panel(
            "GitHub: https://github.com/Insight-Services-APAC/ingenious",
            title="📖 Documentation",
            border_style="blue",
        )
        self.console.print(docs_panel)

    def _show_setup_help(self) -> None:
        """Show setup-specific help."""
        content = (
            "To set up your Insight Ingenious project:\n\n"
            "1. Run `ingen init` to generate project files\n"
            "2. Configure API keys and settings in `.env`\n"
            "3. Update `config.yml` and `profiles.yml` as needed\n"
            "4. Set environment variables:\n"
            "   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml\n"
            "   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml\n"
            "5. Start the server with `ingen serve`"
        )

        panel = Panel(content, title="🛠️  Project Setup Guide", border_style="blue")
        self.console.print(panel)

    def _show_workflows_help(self) -> None:
        """Show workflows-specific help."""
        content = (
            "Workflows are the core of Insight Ingenious. They define how agents\n"
            "process and respond to user inputs.\n\n"
            "Use 'ingen workflows' to see all available workflows and their requirements."
        )

        panel = Panel(content, title="🔄 Workflows Guide", border_style="blue")
        self.console.print(panel)

    def _show_config_help(self) -> None:
        """Show configuration-specific help."""
        content = (
            "Configuration is split between two files:\n"
            "• config.yml - Non-sensitive project settings\n"
            "• profiles.yml - API keys and sensitive configuration"
        )

        panel = Panel(content, title="⚙️  Configuration Guide", border_style="blue")
        self.console.print(panel)

    def _show_deployment_help(self) -> None:
        """Show deployment-specific help."""
        content = (
            "Insight Ingenious can be deployed in several ways:\n"
            "• Local development: ingen serve\n"
            "• Docker: Use provided Docker templates\n"
            "• Cloud: Deploy to Azure, AWS, or other cloud providers"
        )

        panel = Panel(content, title="🚀 Deployment Guide", border_style="blue")
        self.console.print(panel)
