"""Status CLI command for Insight Ingenious.

This module contains the status command for checking system configuration.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from rich.panel import Panel

from ingenious.cli.base import BaseCommand
from ingenious.cli.utilities import OutputFormatters


class StatusCommand(BaseCommand):
    """Check system status and configuration."""

    def execute(self, **kwargs: Any) -> None:
        """Check the status of Insight Ingenious configuration.

        Validates:
        • Configuration files existence and validity
        • Environment variables
        • Required dependencies
        • Available workflows
        """
        self.console.print("[bold blue]🔍 Insight Ingenious System Status[/bold blue]\n")

        status_items: dict[str, Any] = {}

        # Check environment variables
        self._check_environment_variables(status_items)

        # Check local files
        self._check_local_files(status_items)

        # Display status table
        table = OutputFormatters.create_status_table(status_items, "System Status")
        self.console.print(table)

        # Show recommendations if needed
        self._show_recommendations(status_items)

    def _check_environment_variables(self, status_items: dict[str, object]) -> None:
        """Check environment variables status."""
        project_path = os.getenv("INGENIOUS_PROJECT_PATH")
        profile_path = os.getenv("INGENIOUS_PROFILE_PATH")

        if project_path:
            if Path(project_path).exists():
                status_items["INGENIOUS_PROJECT_PATH"] = {
                    "status": "OK",
                    "details": project_path,
                }
            else:
                status_items["INGENIOUS_PROJECT_PATH"] = {
                    "status": "Warning",
                    "details": f"File not found: {project_path}",
                }
        else:
            status_items["INGENIOUS_PROJECT_PATH"] = {
                "status": "Missing",
                "details": "Environment variable not set",
            }

        if profile_path:
            if Path(profile_path).exists():
                status_items["INGENIOUS_PROFILE_PATH"] = {
                    "status": "OK",
                    "details": profile_path,
                }
            else:
                status_items["INGENIOUS_PROFILE_PATH"] = {
                    "status": "Warning",
                    "details": f"File not found: {profile_path}",
                }
        else:
            status_items["INGENIOUS_PROFILE_PATH"] = {
                "status": "Missing",
                "details": "Environment variable not set",
            }

    def _check_local_files(self, status_items: dict[str, object]) -> None:
        """Check local configuration files."""
        files_to_check = {
            "config.yml": Path.cwd() / "config.yml",
            "profiles.yml": Path.cwd() / "profiles.yml",
            ".env": Path.cwd() / ".env",
        }

        for name, path in files_to_check.items():
            if path.exists():
                status_items[f"Local {name}"] = {"status": "OK", "details": str(path)}
            else:
                status_items[f"Local {name}"] = {
                    "status": "Missing",
                    "details": "File not found in current directory",
                }

    def _show_recommendations(self, status_items: dict[str, object]) -> None:
        """Show setup recommendations based on status."""
        has_issues = any(
            item.get("status", "").lower() in ["missing", "warning", "error"]
            for item in status_items.values()
            if isinstance(item, dict)
        )

        if has_issues:
            recommendations = [
                "export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml",
                "export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml",
            ]

            if any("Missing" in str(item) for item in status_items.values()):
                recommendations.insert(0, "ingen init  # Initialize missing files")

            panel = Panel(
                "\n".join(recommendations),
                title="💡 Quick Setup Recommendations",
                border_style="yellow",
            )
            self.console.print("\n")
            self.console.print(panel)
