"""UV Tool environment utilities for WL Commands."""

import os
import sys
from pathlib import Path
from typing import Optional


def is_running_in_uv_tool() -> bool:
    """Check if we are running in a UV Tool environment.

    Returns:
        bool: True if running in UV Tool environment, False otherwise.
    """
    return "UV_TOOL_DIR" in os.environ or "UV_PYTHON" in os.environ


def get_uv_tool_python_path() -> str | None:
    """Get the Python executable path from UV Tool environment.

    Returns:
        Optional[str]: Python executable path if in UV Tool environment, None otherwise.
    """
    if "UV_PYTHON" in os.environ:
        return os.environ["UV_PYTHON"]

    if "UV_TOOL_DIR" in os.environ:
        # Try to find python executable in UV tool directory
        uv_tool_dir = Path(os.environ["UV_TOOL_DIR"])
        python_executable = uv_tool_dir.parent.parent / "python"
        if python_executable.exists():
            return str(python_executable)

        # Try Windows-specific path
        python_executable = uv_tool_dir.parent.parent / "python.exe"
        if python_executable.exists():
            return str(python_executable)

    return None


def get_uv_tool_bin_path() -> Path | None:
    """Get the bin directory path from UV Tool environment.

    Returns:
        Optional[Path]: Bin directory path if in UV Tool environment, None otherwise.
    """
    if "UV_TOOL_DIR" in os.environ:
        uv_tool_dir = Path(os.environ["UV_TOOL_DIR"])
        return uv_tool_dir

    return None


def get_uv_tool_env() -> dict[str, str]:
    """Get environment variables for UV Tool environment.

    Returns:
        dict[str, str]: Environment variables for UV Tool environment.
    """
    env = os.environ.copy()

    # Add UV Tool bin directory to PATH if not already present
    uv_tool_bin = get_uv_tool_bin_path()
    if uv_tool_bin:
        path = env.get("PATH", "")
        if str(uv_tool_bin) not in path:
            env["PATH"] = f"{uv_tool_bin}{os.pathsep}{path}"

    return env


def should_use_direct_execution(command: list[str]) -> bool:
    """Check if a command should be executed directly in UV Tool environment.

    Args:
        command: Command to check.

    Returns:
        bool: True if command should be executed directly, False otherwise.
    """
    if not is_running_in_uv_tool():
        return False

    # Check if it's an 'uv run' command
    if len(command) >= 2 and command[0] == "uv" and command[1] == "run":
        return True

    return False


def get_direct_command(command: list[str]) -> list[str]:
    """Get the direct command by removing 'uv run' prefix.

    Args:
        command: Original command with 'uv run' prefix.

    Returns:
        list[str]: Command without 'uv run' prefix.
    """
    if len(command) >= 2 and command[0] == "uv" and command[1] == "run":
        return command[2:]
    return command
