#!/usr/bin/env python3
"""
Python wrapper for pre-commit hook.
"""

import os
import subprocess
import sys


def main():
    """Main function to execute pre-commit hook."""
    print("✓ Pre-commit hook is running...")
    print("✓ Pre-commit钩子正在运行...")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Try to find uv Python interpreter
    uv_python = None

    # Try direct uv call first
    try:
        uv_python = subprocess.check_output(
            ["uv", "python", "--print-path"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        pass

    # If uv Python not found, try common virtual environment paths
    if not uv_python:
        venv_paths = [
            "./.venv/bin/python",
            "./.venv/bin/python3",
            "../.venv/bin/python",
            "../.venv/bin/python3",
            ".venv/Scripts/python.exe",
            ".venv/Scripts/python3.exe",
            "../.venv/Scripts/python.exe",
            "../.venv/Scripts/python3.exe",
        ]

        for path in venv_paths:
            abs_path = os.path.join(os.getcwd(), path)
            if os.path.exists(abs_path):
                uv_python = abs_path
                break

    if not uv_python:
        print(
            "Error: Could not find Python interpreter. Please ensure uv is installed.",
            file=sys.stderr,
        )
        return 1

    # Execute the original shell hook with uv Python
    result = subprocess.run(
        [
            uv_python,
            "-m",
            "pre_commit",
            "hook-impl",
            "--config=.wl/.pre-commit-config.yaml",
            "--hook-type=pre-commit",
            "--hook-dir",
            script_dir,
            "--",
        ]
        + sys.argv[1:],
        capture_output=True,
        text=True,
    )

    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
