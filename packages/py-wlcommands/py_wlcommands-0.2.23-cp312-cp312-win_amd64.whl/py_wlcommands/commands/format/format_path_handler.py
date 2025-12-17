"""Format path handler module."""

import os
from pathlib import Path

from ...utils.logging import log_info
from .python_formatter import (
    _run_format_command,
    format_with_python_tools,
)
from .rust_formatter import format_rust_code


class FormatPathHandler:
    """Handler for formatting paths."""

    def format_specified_paths(self, paths, env, quiet, unsafe=False):
        """Format specified paths."""
        from pathlib import Path as PathClass

        for path in paths:
            # Convert to Path object if needed
            if (
                hasattr(path, "exists")
                and hasattr(path, "is_file")
                and hasattr(path, "is_dir")
                and hasattr(path, "name")
            ):
                path_obj = path
            else:
                path_obj = PathClass(path)

            if path_obj.exists():
                if path_obj.is_file() and path_obj.suffix == ".py":
                    self._format_python_file(path_obj, path, env, quiet, unsafe)
                elif path_obj.is_dir():
                    self._format_directory(path_obj, path, env, quiet, unsafe)
            else:
                if not quiet:
                    print(f"Warning: Path {path} does not exist")

    def _format_python_file(self, path_obj, original_path, env, quiet, unsafe):
        """Format a single Python file."""
        try:
            # Format with ruff check
            ruff_check_cmd = ["uv", "run", "ruff", "check", "--fix"]
            if unsafe:
                ruff_check_cmd.append("--unsafe-fixes")
            ruff_check_cmd.append(str(path_obj))

            _run_format_command(ruff_check_cmd, env, quiet, passthrough=not quiet)

            # Format with ruff format
            _run_format_command(
                [
                    "uv",
                    "run",
                    "ruff",
                    "format",
                    str(path_obj),
                ],
                env,
                quiet,
                passthrough=not quiet,
            )

            # Run pre-commit on the file - this will handle trailing whitespace and end-of-file fixes
            # and ensure consistent formatting according to the project's pre-commit configuration
            self._run_pre_commit_on_file(path_obj, original_path, env, quiet)
        except Exception as e:
            if not quiet:
                print(f"Warning: Failed to format {original_path}: {e}")

    def _format_directory(self, path_obj, original_path, env, quiet, unsafe):
        """Format a directory."""
        # Format with Python tools
        format_with_python_tools(str(path_obj), env, quiet, unsafe=unsafe)

        # Special handling for rust directory
        if path_obj.name == "rust":
            format_rust_code(str(path_obj), env, quiet)

        # Run pre-commit on the directory
        self._run_pre_commit_on_directory(path_obj, original_path, env, quiet)

    def _run_pre_commit_on_file(self, path_obj, original_path, env, quiet):
        """Run pre-commit on a single file."""
        from ...utils.subprocess_utils import SubprocessExecutor

        try:
            executor = SubprocessExecutor()

            # Find the pre-commit config path
            precommit_config_path = ".pre-commit-config.yaml"
            if not os.path.exists(precommit_config_path):
                precommit_config_path = ".wl/.pre-commit-config.yaml"

            # Only run pre-commit if config exists
            if os.path.exists(precommit_config_path):
                command = [
                    "uv",
                    "run",
                    "pre-commit",
                    "run",
                    "--files",
                    str(path_obj),
                    "--config",
                    precommit_config_path,
                ]

                # Execute pre-commit directly with SubprocessExecutor to handle its exit codes properly
                # Pre-commit returns non-zero exit code if it fixes issues, which is expected behavior
                result = executor.run(command, env=env, quiet=quiet)

                # Always log that pre-commit was run, regardless of exit code
                if not quiet and result.stdout:
                    print(result.stdout)

        except Exception as e:
            if not quiet:
                print(f"Warning: Pre-commit failed for {original_path}: {e}")

    def _run_pre_commit_on_directory(self, path_obj, original_path, env, quiet):
        """Run pre-commit on a directory."""
        from ...utils.subprocess_utils import SubprocessExecutor

        try:
            executor = SubprocessExecutor()

            # Find the pre-commit config path
            precommit_config_path = ".pre-commit-config.yaml"
            if not os.path.exists(precommit_config_path):
                precommit_config_path = ".wl/.pre-commit-config.yaml"

            # Only run pre-commit if config exists
            if os.path.exists(precommit_config_path):
                command = [
                    "uv",
                    "run",
                    "pre-commit",
                    "run",
                    "--all-files",
                    "--config",
                    precommit_config_path,
                ]

                # Execute pre-commit directly with SubprocessExecutor to handle its exit codes properly
                # Pre-commit returns non-zero exit code if it fixes issues, which is expected behavior
                result = executor.run(command, env=env, quiet=quiet)

                # Always log that pre-commit was run, regardless of exit code
                if not quiet and result.stdout:
                    print(result.stdout)

        except Exception as e:
            if not quiet:
                print(f"Warning: Pre-commit failed for {original_path}: {e}")

    def format_defaults(
        self, current_path: Path, env: dict, quiet: bool, unsafe: bool, for_lint: bool
    ) -> None:
        src_path = current_path / "src"
        tools_path = current_path / "tools"
        examples_path = current_path / "examples"
        tests_path = current_path / "tests"
        rust_path = current_path / "rust"
        if src_path.exists():
            log_info("Formatting src directory...")
            format_with_python_tools(str(src_path), env, quiet, unsafe=unsafe)
        if tools_path.exists():
            log_info("Formatting tools directory...")
            format_with_python_tools(str(tools_path), env, quiet, unsafe=unsafe)
        if examples_path.exists():
            log_info("Formatting examples directory...")
            format_with_python_tools(str(examples_path), env, quiet, unsafe=unsafe)
        if tests_path.exists():
            log_info("Formatting tests directory...")
            format_with_python_tools(str(tests_path), env, quiet, unsafe=unsafe)
        # Type stubs generation removed from format; handled in build dist
        if rust_path.exists() and not for_lint:
            log_info("Formatting Rust code...")
            format_rust_code(str(rust_path), env, quiet)

        # Note: We no longer manually handle trailing whitespace and end-of-file newlines here
        # because pre-commit's trailing-whitespace and end-of-file-fixer hooks already handle this
        # This ensures consistency between wl format and running pre-commit directly

        # Run pre-commit on all files
        try:
            # Check if .pre-commit-config.yaml exists in current directory or .wl directory
            precommit_config_path = ".pre-commit-config.yaml"
            if not os.path.exists(precommit_config_path):
                precommit_config_path = ".wl/.pre-commit-config.yaml"

            if os.path.exists(precommit_config_path):
                log_info("Running pre-commit hooks...")
                from ...utils.subprocess_utils import SubprocessExecutor

                executor = SubprocessExecutor()
                command = [
                    "uv",
                    "run",
                    "pre-commit",
                    "run",
                    "--all-files",
                    "--config",
                    precommit_config_path,
                ]

                # Execute pre-commit directly with SubprocessExecutor to handle its exit codes properly
                # Pre-commit returns non-zero exit code if it fixes issues, which is expected behavior
                result = executor.run(command, env=env, quiet=quiet)

                # Always log that pre-commit was run, regardless of exit code
                if not quiet and result.stdout:
                    print(result.stdout)
            else:
                if not quiet:
                    print(
                        "Warning: .pre-commit-config.yaml not found in current directory or .wl directory, skipping pre-commit hooks"
                    )
        except Exception as e:
            if not quiet:
                print(f"Warning: Pre-commit hooks failed: {e}")
