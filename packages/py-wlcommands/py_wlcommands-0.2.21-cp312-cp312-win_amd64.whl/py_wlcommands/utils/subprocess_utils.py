"""Unified subprocess execution utilities for WL Commands."""

import os
import subprocess
import sys
from pathlib import Path

from .file_operations import get_file_operations


class SubprocessResult:
    """Result of a subprocess execution."""

    def __init__(self, returncode: int, stdout: str, stderr: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    @property
    def success(self) -> bool:
        """Check if the subprocess execution was successful."""
        return self.returncode == 0


class SubprocessExecutor:
    """Unified subprocess executor with caching and async capabilities."""

    def __init__(self):
        self._command_cache: dict[str, SubprocessResult] = {}
        self._file_ops = get_file_operations()

    def run(
        self,
        command: list[str],
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
        cache_result: bool = False,
        quiet: bool = False,
    ) -> SubprocessResult:
        """
        Run a subprocess command.

        Args:
            command: The command to execute as a list of strings
            env: Environment variables to use
            cwd: Current working directory
            cache_result: Whether to cache the result
            quiet: Whether to suppress output

        Returns:
            SubprocessResult: The result of the subprocess execution
        """
        command_key = " ".join(command)

        # Return cached result if available
        if cache_result and command_key in self._command_cache:
            return self._command_cache[command_key]

        # Prepare environment variables: preserve current process env if None
        environment = env.copy() if env is not None else os.environ.copy()

        # Fix encoding issues on Windows
        if sys.platform.startswith("win"):
            environment["PYTHONIOENCODING"] = "utf-8"
            environment["PYTHONLEGACYWINDOWSFSENCODING"] = "1"

        try:
            if quiet:
                # Capture output to suppress it
                result = subprocess.run(
                    command,
                    env=environment,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    shell=False,
                    encoding="utf-8" if sys.platform.startswith("win") else None,
                )
            else:
                # Let the command output directly to stdout/stderr
                result = subprocess.run(
                    command,
                    env=environment,
                    cwd=cwd,
                    shell=False,
                    encoding="utf-8" if sys.platform.startswith("win") else None,
                )

            sub_result = SubprocessResult(
                returncode=result.returncode,
                stdout=result.stdout if result.stdout else "",
                stderr=result.stderr if result.stderr else "",
            )

            # Cache the result if requested
            if cache_result:
                self._command_cache[command_key] = sub_result

            return sub_result

        except Exception as e:
            # Return a failed result in case of exception
            sub_result = SubprocessResult(returncode=-1, stdout="", stderr=str(e))
            return sub_result

    def clear_cache(self) -> None:
        """Clear the command cache."""
        self._command_cache.clear()

    def get_cached_commands(self) -> list[str]:
        """Get a list of cached command keys."""
        return list(self._command_cache.keys())
