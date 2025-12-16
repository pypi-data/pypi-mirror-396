"""Help and status CLI commands for Insight Ingenious.

This module has been refactored into separate command files for better maintainability.
All public APIs remain unchanged for backward compatibility.
"""

from __future__ import annotations

from typing import Any

# Import command classes from separate files
from ingenious.cli.commands.help_command import HelpCommand
from ingenious.cli.commands.status_command import StatusCommand
from ingenious.cli.commands.validate_command import ValidateCommand
from ingenious.cli.commands.version_command import VersionCommand

__all__ = [
    "HelpCommand",
    "StatusCommand",
    "VersionCommand",
    "ValidateCommand",
    "register_commands",
]


# Command registration functions for backward compatibility
def register_commands(app: Any, console: Any) -> None:
    """Register help commands with the typer app."""
    import typer
    from typing_extensions import Annotated

    @app.command(name="help", help="Show detailed help and getting started guide")  # type: ignore[misc]
    def help_command(
        topic: Annotated[
            str | None,
            typer.Argument(help="Specific topic: setup, workflows, config, deployment"),
        ] = None,
    ) -> None:
        """Show comprehensive help for getting started with Insight Ingenious."""
        cmd = HelpCommand(console)
        cmd.run(topic=topic)

    @app.command(name="status", help="Check system status and configuration")  # type: ignore[misc]
    def status() -> None:
        """Check the status of your Insight Ingenious configuration."""
        cmd = StatusCommand(console)
        cmd.run()

    @app.command(name="version", help="Show version information")  # type: ignore[misc]
    def version() -> None:
        """Display version information for Insight Ingenious."""
        cmd = VersionCommand(console)
        cmd.run()

    @app.command(name="validate", help="Validate system configuration and requirements")  # type: ignore[misc]
    def validate() -> None:
        """Comprehensive validation of your Insight Ingenious setup."""
        cmd = ValidateCommand(console)
        cmd.run()
