"""Lint command module."""

from pathlib import Path
from typing import Any

from ...commands import Command, register_command
from .lint_command import LintCommandImpl


@register_command("lint")
class LintCommand(Command):
    """Command to lint code."""

    def __init__(self):
        """Initialize the lint command."""
        self._impl = LintCommandImpl()

    @property
    def name(self) -> str:
        """Return the command name."""
        return self._impl.name

    @property
    def help(self) -> str:
        """Return the command help text."""
        return self._impl.help

    def add_arguments(self, parser: Any) -> None:
        """Add command-specific arguments."""
        self._impl.add_arguments(parser)

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Execute the lint command."""
        self._impl.execute(*args, **kwargs)
