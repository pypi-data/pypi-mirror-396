"""Format command module."""

import argparse
import sys
from pathlib import Path

from ...commands import register_command
from ...commands.base import BaseCommand
from .format_coordinator import FormatCoordinator


@register_command("format")
class FormatCommand(BaseCommand):
    """Command to format code."""

    def __init__(self):
        """Initialize the format command."""
        self.coordinator = FormatCoordinator()

    def run(self, *args, **kwargs):
        """Run the format command with lifecycle and error handling."""
        return super().run(*args, **kwargs)

    @property
    def name(self) -> str:
        return "format"

    @property
    def help(self) -> str:
        return "Format code with ruff and cargo fmt"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        self.coordinator.add_arguments(parser)

    def execute(self, *args, **kwargs):
        """Execute the format command."""
        self.coordinator.execute(*args, **kwargs)
