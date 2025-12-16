"""Stage executor utilities for orchestrating multi-step operations with progress tracking.

Provides abstractions for executing staged operations with Rich console output,
progress tracking, and logging integration.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn

from ingenious.utils.log_levels import LogLevel


class IActionCallable(ABC):
    """Abstract base class for action callables in stage execution.

    Action callables are invoked during stage execution and receive progress
    tracking capabilities.
    """

    @abstractmethod
    async def __call__(
        self, progress: "ProgressConsoleWrapper", task_id: TaskID, **kwargs: Any
    ) -> None:
        """Execute the action.

        Args:
            progress: Wrapped progress object for console output.
            task_id: The task ID for progress tracking.
            **kwargs: Additional keyword arguments.
        """
        pass


class ProgressConsoleWrapper:
    """Wrapper for Rich Progress object with logging integration.

    Provides a convenient interface for printing messages with log levels
    and tracking completion statistics.

    Attributes:
        progress: The Rich Progress object.
        log_level: The minimum log level to display messages.
    """

    def __init__(self, progress: Progress, log_level: int) -> None:
        """Initialize the progress console wrapper.

        Args:
            progress: The Rich Progress object to wrap.
            log_level: The minimum log level to display messages.
        """
        self.progress: Progress = progress
        self.log_level: int = log_level
        self._completed_items: int = 0
        self._failed_items: int = 0

    def print(self, message: str, level: int = LogLevel.INFO, *args: Any, **kwargs: Any) -> None:
        """Print a message to the console if log level permits.

        Args:
            message: The message to print.
            level: The log level of the message.
            *args: Additional positional arguments for console.print.
            **kwargs: Additional keyword arguments for console.print.
        """
        if level >= self.log_level:
            # Check if style is in args or kwargs
            style: Optional[str] = kwargs.get("style", None)
            if style is None:
                # get the string representation of the level
                style = LogLevel.to_string(level).lower()
            # Add the style to the kwargs
            kwargs["style"] = style
            self.progress.console.print(message, *args, **kwargs)

    @property
    def completed_items(self) -> int:
        """Get the count of completed items."""
        return self._completed_items

    @completed_items.setter
    def completed_items(self, value: int) -> None:
        """Set the count of completed items."""
        self._completed_items = value

    @property
    def failed_items(self) -> int:
        """Get the count of failed items."""
        return self._failed_items

    @failed_items.setter
    def failed_items(self, value: int) -> None:
        """Set the count of failed items."""
        self._failed_items = value

    def __getattr__(self, attr: str) -> Any:
        """Proxy attribute access to the underlying Progress object."""
        return getattr(self.progress, attr)


class stage_executor:
    """Executor for multi-step operations with progress tracking.

    Attributes:
        log_level: The minimum log level to display.
        console: The Rich console for output.
    """

    def __init__(self, log_level: int, console: Console) -> None:
        """Initialize the stage executor.

        Args:
            log_level: The minimum log level to display.
            console: The Rich console for output.
        """
        self.log_level: int = log_level
        self.console: Console = console

    async def perform_stage(
        self,
        option: bool = True,
        action_callables: Optional[List[IActionCallable]] = None,
        stage_name: str = "Stage - No Name Provided",
        **kwargs: Any,
    ) -> None:
        """Perform a stage with the given action callables.

        Args:
            option: Whether to execute the stage or skip it.
            action_callables: List of callables implementing IActionCallable.
            stage_name: The name of the stage for display.
            **kwargs: Additional keyword arguments passed to action callables.
        """
        if action_callables is None:
            action_callables = []

        with Progress(
            SpinnerColumn(spinner_name="dots", style="progress.spinner", finished_text="📦"),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
            console=self.console,
        ) as progress:
            stage_status: str = "Initiated  "

            # progress.console.print(Panel(f"Stage: {stage_name}"))
            ptid: TaskID = progress.add_task(description=f"[{stage_status}] Stage: {stage_name}")
            # Wrap the Progress object
            wrapped_progress: ProgressConsoleWrapper = ProgressConsoleWrapper(
                progress, self.log_level
            )

            start: float = time.time()
            if option:
                stage_status = "Running  🏃‍♂️"
                progress.update(task_id=ptid, description=f"[{stage_status}] Stage: {stage_name}")
                for action_callable in action_callables:
                    await action_callable.__call__(
                        progress=wrapped_progress, task_id=ptid, **kwargs
                    )
                stage_status = "Completed ✅ "
                progress.update(task_id=ptid, description=f"[{stage_status}] Stage: {stage_name}")
            else:
                stage_status = "Skipped  -- "
                progress.update(task_id=ptid, description=f"[{stage_status}] Stage: {stage_name}")
            time.sleep(1)  # Simulate some delay
            runtime: float = time.time() - start
            milliseconds: int = int((runtime % 1) * 1000)
            runtime_str: str = (
                time.strftime("%H:%M:%S", time.gmtime(runtime)) + f".{milliseconds:03d}"
            )
            progress.update(
                task_id=ptid,
                description=f"[{stage_status}] Stage: {stage_name}[info] | Runtime: {runtime_str}[/info]",
                total=1,
                completed=1,
            )
