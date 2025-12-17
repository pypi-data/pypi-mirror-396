"""Lint command implementation."""

import sys
from argparse import ArgumentParser
from pathlib import Path

from ...utils.logging import log_info
from ...utils.project_root import find_project_root
from ...utils.subprocess_utils import SubprocessResult
from .lint_executor import LintExecutor
from .lint_formatter import LintFormatter
from .lint_reporter import LintReporter


class LintCommandImpl:
    """Implementation of the lint command."""

    def __init__(self):
        """Initialize the lint command implementation."""
        self.executor = LintExecutor()
        self.formatter = LintFormatter()
        self.reporter = LintReporter()

    @property
    def name(self) -> str:
        return "lint"

    @property
    def help(self) -> str:
        return "Lint code with ruff - equivalent to make lint"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "paths", nargs="*", help="Paths to lint (default: current directory)"
        )
        parser.add_argument(
            "-q", "--quiet", action="store_true", help="Suppress detailed output"
        )
        parser.add_argument(
            "--fix", action="store_true", help="Automatically fix lint errors"
        )
        parser.add_argument(
            "--noreport",
            action="store_true",
            help="Do not generate lint report in todos folder",
        )
        parser.add_argument(
            "--report",
            action="store_true",
            help="Generate lint report in todos folder",
        )

    def execute(
        self,
        paths: list[str] | None = None,
        quiet: bool = False,
        fix: bool = False,
        noreport: bool = False,
        report: bool = False,
        **kwargs: dict[str, object],
    ) -> None:
        """
        Lint code - equivalent to make lint
        代码静态检查 - 等效于 make lint
        """
        # 忽略传递的额外参数，例如'command'
        # Ignore extra arguments passed, such as 'command'

        if not quiet:
            self._log_info("Linting code...", "正在进行代码静态检查...")

        try:
            # Get project root directory
            project_root = find_project_root()

            # First, format the code
            # 首先，格式化代码
            self.formatter.format_code(project_root, paths, quiet)

            # Prepare and run ruff command
            cmd = self.executor.prepare_ruff_command(paths, fix, quiet)

            result = self.executor.run_ruff_command(cmd, project_root, quiet, noreport)

            # Generate report if requested (default behavior)
            if report or not noreport:
                self.reporter.generate_report(result, project_root, quiet, paths, fix)

            # Handle result
            self._handle_result(result, quiet)

            # 如果有错误，退出码非0
            if result.returncode != 0:
                sys.exit(result.returncode)

        except FileNotFoundError:
            self._handle_file_not_found_error(quiet)
            sys.exit(1)
        except Exception as e:
            self._handle_general_error(e, quiet)
            sys.exit(1)

    def _get_project_root(self) -> Path:
        """Get the project root directory by looking for pyproject.toml file."""
        return find_project_root()

    def _log_info(self, en_msg: str, zh_msg: str) -> None:
        """Log info message in both English and Chinese."""
        log_info(en_msg, lang="en")
        log_info(zh_msg, lang="zh")

    def _handle_result(self, result: SubprocessResult, quiet: bool) -> None:
        """Handle the result of the linting process."""
        if result.returncode != 0 and not quiet:
            self._log_info(
                "Linting completed with issues:", "代码静态检查发现以下问题:"
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        elif result.returncode == 0 and not quiet:
            self._log_info(
                "Code linting completed successfully!", "代码静态检查成功完成！"
            )

    def _handle_file_not_found_error(self, quiet: bool) -> None:
        """Handle FileNotFoundError."""
        if not quiet:
            self._log_info(
                "Error: ruff is not installed or not found in PATH",
                "错误：未安装 ruff 或在 PATH 中找不到",
            )

    def _handle_general_error(self, e: Exception, quiet: bool) -> None:
        """Handle general exceptions."""
        if not quiet:
            self._log_info(f"Error during linting: {e}", f"错误：静态检查期间出错: {e}")
