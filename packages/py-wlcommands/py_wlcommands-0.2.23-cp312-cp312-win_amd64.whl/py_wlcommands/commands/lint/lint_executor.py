"""
Lint executor module.
Handles execution of ruff commands.
"""

from pathlib import Path

from ...utils.subprocess_utils import SubprocessExecutor, SubprocessResult


class LintExecutor:
    """Executor for lint commands."""

    def prepare_ruff_command(
        self, paths: list[str] | None, fix: bool, quiet: bool
    ) -> list[str]:
        """Prepare the ruff command."""
        # Prepare ruff command (offline, no uv fetch)
        cmd = ["ruff", "check"]

        # Add paths to lint or default to current directory
        if paths:
            existing = []
            for p in paths:
                try:
                    if Path(p).exists():
                        existing.append(p)
                except Exception:
                    pass
            if existing:
                cmd.extend(existing)
            else:
                cmd.append(".")
        else:
            cmd.append(".")

        # Add fix flag if requested
        if fix:
            cmd.append("--fix")

        # Add quiet flag if requested
        if quiet:
            cmd.append("--quiet")

        return cmd

    def run_ruff_command(
        self, cmd: list[str], project_root: Path, quiet: bool, noreport: bool
    ) -> SubprocessResult:
        """Run the ruff command and return the result (统一子进程执行)."""
        executor = SubprocessExecutor()
        capture = quiet or not noreport
        return executor.run(command=cmd, cwd=project_root, quiet=capture)
