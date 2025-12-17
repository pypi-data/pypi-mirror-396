"""
Python code formatting utilities for WL Commands."""

import os
import subprocess
from pathlib import Path

from ...utils.subprocess_utils import SubprocessExecutor


def _run_format_command(
    command: list, env: dict, quiet: bool, passthrough: bool = False
) -> None:
    """Run a formatting command with proper output handling."""
    # Use SubprocessExecutor for consistent command execution
    executor = SubprocessExecutor()

    # Execute the command - SubprocessExecutor handles UV Tool environment automatically
    result = executor.run(command, env=env, quiet=not passthrough)

    # Fallback: if uv is missing and command was 'uv run ...', try direct execution
    if (
        len(command) >= 2
        and command[0] == "uv"
        and command[1] == "run"
        and not result.success
        and (
            "No such file or directory" in result.stderr or "not found" in result.stderr
        )
        and "uv" in result.stderr
    ):
        try:
            direct_command = command[2:]
            result = executor.run(direct_command, env=env, quiet=not passthrough)
        except Exception:
            pass

    # Handle command failure - only log the error, don't raise exception
    if not result.success:
        error_msg = f"Command failed with return code {result.returncode}"
        if result.stderr:
            error_msg += f": {result.stderr.strip()}"
        if not quiet:
            print(f"Warning: {error_msg}")


def format_with_ruff(
    directory: str, env: dict, quiet: bool = False, unsafe: bool = False
) -> None:
    """Format directory with ruff only."""
    try:
        # Run ruff check with fix
        ruff_check_cmd = ["uv", "run", "ruff", "check", "--fix"]
        if unsafe:
            ruff_check_cmd.append("--unsafe-fixes")
        ruff_check_cmd.append(directory)

        _run_format_command(ruff_check_cmd, env, quiet, passthrough=not quiet)

        # Run ruff format for code formatting
        _run_format_command(
            [
                "uv",
                "run",
                "ruff",
                "format",
                directory,
            ],
            env,
            quiet,
            passthrough=not quiet,
        )

        # Note: We no longer manually handle trailing whitespace and end-of-file newlines here
        # because pre-commit's trailing-whitespace and end-of-file-fixer hooks should handle this
        # This ensures consistency between wl format and running pre-commit directly
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"Warning: ruff formatting failed with return code {e.returncode}")
        raise
    except FileNotFoundError as e:
        if not quiet:
            print(f"Warning: uv or ruff not found in PATH: {e}")
    except Exception as e:
        if not quiet:
            print(f"Warning occurred during ruff formatting: {e}")


def format_with_python_tools(
    directory: str, env: dict, quiet: bool = False, unsafe: bool = False
) -> None:
    """Format directory with Python tools (ruff only)."""
    try:
        # Format with ruff only
        format_with_ruff(directory, env, quiet, unsafe)
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"Warning: Python formatting failed with return code {e.returncode}")
        raise
    except Exception as e:
        if not quiet:
            print(f"Warning occurred during Python formatting: {e}")


def format_tools_scripts(
    tools_dir: str, env: dict, quiet: bool, unsafe: bool = False
) -> None:
    """Format Python files in tools directory with ruff."""
    tools_path = Path(tools_dir)
    if not tools_path.exists():
        if not quiet:
            print(f"Tools directory {tools_dir} does not exist, skipping...")
        return

    # Find all Python files in tools directory
    python_files = list(tools_path.glob("**/*.py"))
    if python_files:
        # Fix issues in tools Python files with ruff check
        try:
            ruff_check_cmd = ["uv", "run", "ruff", "check", "--fix"]
            if unsafe:
                ruff_check_cmd.append("--unsafe-fixes")
            ruff_check_cmd.extend([str(f) for f in python_files])

            _run_format_command(ruff_check_cmd, env, quiet, passthrough=not quiet)
        except Exception as e:
            if not quiet:
                print(f"Warning: ruff check failed for tools scripts: {e}")

        # Format tools Python files with ruff format
        try:
            _run_format_command(
                ["uv", "run", "ruff", "format"] + [str(f) for f in python_files],
                env,
                quiet,
                passthrough=not quiet,
            )
        except Exception as e:
            if not quiet:
                print(f"Warning: ruff format failed for tools scripts: {e}")
    else:
        if not quiet:
            print("No Python files found in tools directory")


def format_examples(
    examples_dir: str, env: dict, quiet: bool, unsafe: bool = False
) -> None:
    """Format examples directory with ruff."""
    examples_path = Path(examples_dir)
    if not examples_path.exists():
        if not quiet:
            print(f"Examples directory {examples_dir} does not exist, skipping...")
        return

    # Fix issues in examples with ruff check
    try:
        ruff_check_cmd = ["uv", "run", "ruff", "check", "--fix"]
        if unsafe:
            ruff_check_cmd.append("--unsafe-fixes")
        ruff_check_cmd.append(examples_dir)

        _run_format_command(ruff_check_cmd, env, quiet, passthrough=not quiet)
    except Exception as e:
        if not quiet:
            print(f"Warning: ruff check failed for examples: {e}")

    # Format examples with ruff format
    try:
        _run_format_command(
            ["uv", "run", "ruff", "format", examples_dir],
            env,
            quiet,
            passthrough=not quiet,
        )
    except Exception as e:
        if not quiet:
            print(f"Warning: ruff format failed for examples: {e}")


def generate_type_stubs(src_dir: str, typings_dir: str, env: dict, quiet: bool) -> None:
    """Generate type stubs."""
    if not quiet:
        print(f"Generating type stubs for {src_dir}...")

    # Ensure typings directory exists
    typings_path = Path(typings_dir)
    typings_path.mkdir(parents=True, exist_ok=True)

    try:
        # Use the full path to python executable to ensure we're using the correct environment
        import sys

        python_executable = sys.executable

        # Make sure the paths are properly escaped for the command
        src_dir_escaped = src_dir.replace("\\", "\\\\")
        typings_dir_escaped = typings_dir.replace("\\", "\\\\")

        cmd = [
            python_executable,
            "-c",
            f"from mypy.stubgen import main; main(['{src_dir_escaped}', '-o', '{typings_dir_escaped}'])",
        ]

        _run_format_command(cmd, env, quiet, passthrough=False)
    except Exception as e:
        if not quiet:
            print(f"Warning: Error generating type stubs: {e}")


__all__ = [
    "_run_format_command",
    "format_with_ruff",
    "format_with_python_tools",
    "format_tools_scripts",
    "format_examples",
    "generate_type_stubs",
]
