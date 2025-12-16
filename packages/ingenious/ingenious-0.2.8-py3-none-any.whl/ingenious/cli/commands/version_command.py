"""Version CLI command for Insight Ingenious.

This module contains the version command for displaying version information.
"""

from __future__ import annotations

from typing import Any

from ingenious.cli.base import BaseCommand


class VersionCommand(BaseCommand):
    """Show version information."""

    def execute(self, **kwargs: Any) -> None:
        """Display version information for Insight Ingenious."""
        try:
            from importlib.metadata import version as get_version

            version_str = get_version("insight-ingenious")
            self.console.print(
                f"[bold blue]Insight Ingenious[/bold blue] version [bold]{version_str}[/bold]"
            )
        except Exception:
            self.console.print("[bold blue]Insight Ingenious[/bold blue] - Development Version")

        self.console.print("🚀 GenAI Accelerator Framework")
        self.console.print("📖 Documentation: https://github.com/Insight-Services-APAC/ingenious")
