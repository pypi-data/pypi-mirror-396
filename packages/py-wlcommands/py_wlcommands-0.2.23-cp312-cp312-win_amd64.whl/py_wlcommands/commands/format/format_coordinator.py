"""Format coordinator module."""

import argparse
import os
import sys
from pathlib import Path

from .format_path_handler import FormatPathHandler
from .format_reporter import FormatReporter


class FormatCoordinator:
    """Coordinator for format command."""

    def __init__(self):
        """Initialize the format coordinator."""
        self.path_handler = FormatPathHandler()
        self.reporter = FormatReporter()

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "-q", "--quiet", action="store_true", help="Suppress detailed output"
        )
        parser.add_argument(
            "--unsafe", action="store_true", help="Enable ruff's unsafe fixes"
        )
        parser.add_argument(
            "--report",
            action="store_true",
            help="Generate format report in todos folder",
        )
        parser.add_argument(
            "paths",
            nargs="*",
            help="Paths to format (default: src, tools, examples, rust)",
        )

    def execute(self, *args, **kwargs):
        """Execute the format command."""
        self._execute_internal(**kwargs)

    def run(self, *args, **kwargs):
        """Run the format command (alias for execute to maintain compatibility)."""
        self._execute_internal(**kwargs)

    def _execute_internal(self, **kwargs):
        """Internal method to execute the format command."""
        quiet = kwargs.get("quiet", False)
        unsafe = kwargs.get("unsafe", True)  # Default to True as per specifications
        report = kwargs.get("report", False)
        paths = kwargs.get("paths", [])
        for_lint = kwargs.get("for_lint", False)

        # Handle --no-unsafe flag if present
        if "no_unsafe" in kwargs:
            unsafe = not kwargs["no_unsafe"]

        env = os.environ.copy()
        current_path = Path.cwd()

        # Handle report generation
        if report:
            self.generate_format_report(quiet, unsafe, paths, env)
            return

        try:
            if paths:
                self.format_specified_paths(paths, env, quiet, unsafe)
            else:
                self.format_defaults(current_path, env, quiet, unsafe, for_lint)
            if not quiet:
                print("Formatting completed.")
        except Exception as e:
            if not quiet:
                print(f"Warning: Error occurred during formatting: {e}")
            sys.exit(1)

    # 添加别名方法以匹配测试期望的接口
    def format_specified_paths(self, paths, env, quiet, unsafe=False):
        """Alias for path_handler.format_specified_paths."""
        self.path_handler.format_specified_paths(paths, env, quiet, unsafe)

    def format_defaults(self, current_path, env, quiet, unsafe, for_lint):
        """Alias for path_handler.format_defaults."""
        self.path_handler.format_defaults(current_path, env, quiet, unsafe, for_lint)

    def generate_format_report(self, quiet, unsafe, paths, env):
        """Alias for reporter.generate_format_report."""
        self.reporter.generate_format_report(quiet, unsafe, paths, env)
