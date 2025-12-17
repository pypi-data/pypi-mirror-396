"""
Lint formatter module.
Handles code formatting before linting.
"""

from pathlib import Path

from ...utils.logging import log_info
from ..format import FormatCommand


class LintFormatter:
    """Formatter for code before linting."""

    def format_code(
        self, project_root: Path, paths: list[str] | None, quiet: bool
    ) -> None:
        """Format code before linting."""
        if not quiet:
            log_info("Formatting code before linting...", "在静态检查前先格式化代码...")

        format_cmd = FormatCommand()
        valid_paths: list[str] | None = None
        if paths:
            filtered = [
                p for p in paths if (project_root / p).exists() or Path(p).exists()
            ]
            valid_paths = filtered if filtered else None
        format_cmd.run(quiet=quiet, unsafe=True, paths=valid_paths, for_lint=True)
