#!/usr/bin/env python3
"""
Check uv.lock consistency and update if needed.
"""

import os
import shutil
import subprocess
import sys


def main():
    """Main function to check uv.lock consistency."""
    # Check if pyproject.toml exists
    if not os.path.exists("pyproject.toml"):
        print("No pyproject.toml found, skipping uv.lock check")
        return 0

    # Generate new lockfile
    result = subprocess.run(
        [
            "uv",
            "pip",
            "compile",
            "pyproject.toml",
            "--quiet",
            "--output-file=uv.lock.new",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Check if uv.lock.new was actually created
        if os.path.exists("uv.lock.new"):
            if os.path.exists("uv.lock"):
                # Compare lockfiles - use platform-specific commands
                if sys.platform.startswith("win"):
                    # Windows uses fc command
                    result = subprocess.run(
                        ["fc", "/b", "uv.lock.new", "uv.lock"],
                        capture_output=True,
                        text=True,
                        shell=True,
                    )
                else:
                    # Unix/Linux/Mac uses diff command
                    result = subprocess.run(
                        ["diff", "-q", "uv.lock.new", "uv.lock"],
                        capture_output=True,
                        text=True,
                    )
                # For both Windows 'fc' and Unix 'diff' commands:
                # - Return code 0 means files are identical
                # - Return code 1 (or other non-zero) means files are different
                if result.returncode != 0:
                    print("Updated uv.lock file")
                    shutil.move("uv.lock.new", "uv.lock")
                else:
                    print("uv.lock file is already consistent")
                    os.remove("uv.lock.new")
            else:
                print("Created uv.lock file")
                shutil.move("uv.lock.new", "uv.lock")
        else:
            print(
                "Error: uv.lock.new was not created by uv pip compile", file=sys.stderr
            )
            return 1
    else:
        print(f"Error: uv pip compile failed: {result.stderr}", file=sys.stderr)
        if os.path.exists("uv.lock.new"):
            os.remove("uv.lock.new")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
