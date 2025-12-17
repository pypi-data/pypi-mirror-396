"""Unified subprocess execution utilities for WL Commands."""

import os
import subprocess
import sys
from pathlib import Path

from .file_operations import get_file_operations
from .uv_tool import (
    get_direct_command,
    get_uv_tool_env,
    is_running_in_uv_tool,
    should_use_direct_execution,
)


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

        # Prepare environment variables
        # Use UV Tool environment if running in UV Tool
        if is_running_in_uv_tool():
            # Start with UV Tool environment
            uv_env = get_uv_tool_env()
            # Update with user-provided environment if any
            if env is not None:
                uv_env.update(env)
            environment = uv_env
        else:
            # Use user-provided environment or system environment
            environment = env.copy() if env is not None else os.environ.copy()

        # Fix encoding issues on Windows
        if sys.platform.startswith("win"):
            environment["PYTHONIOENCODING"] = "utf-8"
            environment["PYTHONLEGACYWINDOWSFSENCODING"] = "1"

        # Determine the actual command to execute
        actual_command = command
        if should_use_direct_execution(command):
            # When running in UV Tool environment, try to run tools directly
            # instead of using uv run to avoid issues
            direct_command = get_direct_command(command)
            try:
                # Try running the command directly first
                if quiet:
                    result = subprocess.run(
                        direct_command,
                        env=environment,
                        cwd=cwd,
                        capture_output=True,
                        text=True,
                        shell=False,
                        encoding="utf-8" if sys.platform.startswith("win") else None,
                    )
                else:
                    result = subprocess.run(
                        direct_command,
                        env=environment,
                        cwd=cwd,
                        shell=False,
                        encoding="utf-8" if sys.platform.startswith("win") else None,
                    )

                # If direct execution succeeded, use this result
                sub_result = SubprocessResult(
                    returncode=result.returncode,
                    stdout=result.stdout if result.stdout else "",
                    stderr=result.stderr if result.stderr else "",
                )

                # Cache the result if requested
                if cache_result:
                    self._command_cache[command_key] = sub_result

                return sub_result
            except Exception:
                # If direct execution fails, fall back to original command
                pass

        # Execute the original command
        try:
            if quiet:
                # Capture output to suppress it
                result = subprocess.run(
                    actual_command,
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
                    actual_command,
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
