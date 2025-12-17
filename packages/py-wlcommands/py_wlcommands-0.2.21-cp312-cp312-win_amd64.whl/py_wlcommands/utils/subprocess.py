"""
Subprocess utilities for WL Commands.
"""

import os
import subprocess
import sys

from ..exceptions import CommandError


def run_command(
    command, env=None, capture_output=False, text=True
) -> subprocess.CompletedProcess:
    """
    Run a command with subprocess.run and handle errors.

    Args:
        command (list): Command to run.
        env (dict, optional): Environment variables. Defaults to None.
        capture_output (bool, optional): Whether to capture output. Defaults to False.
        text (bool, optional): Whether to return text output. Defaults to True.

    Returns:
        subprocess.CompletedProcess: Result of the command.

    Raises:
        CommandError: If the command fails.
    """
    # Prepare environment variables
    environment = env or os.environ.copy()

    # Fix encoding issues on Windows
    if sys.platform.startswith("win"):
        # Set environment variables to ensure proper UTF-8 handling
        environment["PYTHONIOENCODING"] = "utf-8"
        environment["PYTHONLEGACYWINDOWSFSENCODING"] = "1"

    try:
        return subprocess.run(
            command,
            check=True,
            env=environment,
            capture_output=capture_output,
            text=text,
            # Explicitly set encoding for Windows systems
            encoding="utf-8" if text else None,
        )
    except subprocess.CalledProcessError as e:
        raise CommandError(f"Command failed: {e}")
    except FileNotFoundError as e:
        raise CommandError(f"Command not found: {e}")
