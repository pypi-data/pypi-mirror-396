"""
Test command builder utilities for test command.
"""

from pathlib import Path


class TestCommandBuilder:
    """Build pytest command arguments based on configuration."""

    def __init__(self, python_detector):
        """Initialize test command builder.

        Args:
            python_detector: Instance of PythonEnvDetector to get Python executable
        """
        self.python_detector = python_detector

    def build_command_args(
        self, report_mode: bool, args: list[str], debug_mode: bool = False
    ) -> list[str]:
        """Build the command arguments for pytest.

        Args:
            report_mode: Whether to generate detailed reports
            args: Additional pytest arguments
            debug_mode: Whether to run in debug mode

        Returns:
            List of command arguments
        """
        python_executable = self.python_detector.get_python_executable()
        cmd_args: list[str] = [python_executable, "-m", "pytest"]

        # Configure warning behavior based on mode
        if report_mode or debug_mode:
            # In report/debug mode, show all warning details
            cmd_args.append("-W")
            cmd_args.append("always")
            cmd_args.append("-v")
            if report_mode:
                cmd_args.append("--tb=short")  # Show shorter tracebacks for failures
            else:
                cmd_args.append("--tb=long")  # Show full tracebacks in debug mode
        else:
            # In default mode, keep quiet and concise
            cmd_args.append("--tb=no")  # Don't show tracebacks for failures
            cmd_args.append("-q")  # Quiet mode
            cmd_args.append("--no-header")  # Don't show pytest header
            # In concise mode, only show warning categories that should fail the test
            cmd_args.append("-W")
            cmd_args.append("error::DeprecationWarning")
            cmd_args.append("-W")
            cmd_args.append("ignore::UserWarning")
            cmd_args.append("-W")
            cmd_args.append("ignore::RuntimeWarning")

        # Add debug markers if in debug mode
        if debug_mode and "-xvs" not in args:
            cmd_args.extend(
                ["-xvs"]
            )  # Stop at first failure, verbose, show print output

        # Add parallel execution support
        if "-n" not in args and "--numprocesses" not in args and not debug_mode:
            cmd_args.append("-n")
            cmd_args.append("auto")

        has_user_cov = any(arg.startswith("--cov") for arg in args)

        # Add coverage-related arguments regardless of mode
        has_pytest_cov = self._check_pytest_cov()
        if has_pytest_cov and not has_user_cov:
            # Always include coverage collection
            cmd_args.extend(
                [
                    "--cov=py_wlcommands",
                    "--cov-branch",
                    "--cov-context=test",
                    "--cov-report=term-missing:skip-covered",
                ]
            )

        if report_mode:
            # In report mode, generate additional coverage outputs
            todo_dir = Path(self._get_project_root()) / "todos"
            cov_json = str(todo_dir / "coverage.json")
            junit_xml = str(todo_dir / "junit.xml")
            cmd_args.extend(
                [f"--cov-report=json:{cov_json}", f"--junitxml={junit_xml}"]
            )

        # Add any additional user arguments
        if args:
            # Check if any argument looks like a test file/directory path (doesn't start with --)
            has_path_arg = any(not arg.startswith("--") for arg in args)
            cmd_args.extend(args)

            # Only add default test path if not in report mode and no path arguments provided
            if not report_mode and not has_path_arg:
                cmd_args.append("tests/")
        else:
            # If no args provided, add default test path
            cmd_args.append("tests/")

        return cmd_args

    def _check_pytest_cov(self) -> bool:
        """
        Check if pytest-cov plugin is available.

        Returns:
            bool: True if pytest-cov is available, False otherwise
        """
        # 使用try-except来检查pytest_cov是否可以导入
        # 这比subprocess调用更高效，也更容易在测试中被mock
        try:
            # 使用__import__函数动态导入，而不是直接使用import语句
            # 这样可以避免导入错误导致的问题
            __import__("pytest_cov")
            return True
        except ImportError:
            # 如果导入失败，返回False
            return False

    def _get_project_root(self) -> str:
        """
        Get the project root directory.

        Returns:
            str: Path to the project root directory
        """
        try:
            from ...utils.project_root import find_project_root

            cwd = Path.cwd()
            if (cwd / "tests").exists() or (cwd / "src").exists():
                return str(cwd)
            root = find_project_root()
            return str(root)
        except Exception:
            return str(Path.cwd())
