"""
Test command implementation for wl tool.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from ...utils.logging import log_info
from ...utils.project_root import find_project_root
from .. import register_command
from ..base import BaseCommand

# Import modular components
from .python_env_detector import PythonEnvDetector
from .test_command_builder import TestCommandBuilder
from .test_result_handler import TestResultHandler


@register_command("test")
class TestCommand(BaseCommand):
    """Command to run tests for the project."""

    # Tell pytest not to collect this class as a test class
    __test__ = False

    def __init__(self):
        """Initialize TestCommand with modular components."""
        super().__init__()
        self.python_detector = PythonEnvDetector()
        self.command_builder = TestCommandBuilder(self.python_detector)
        self.result_handler = TestResultHandler()

    @property
    def name(self) -> str:
        """Get the command name."""
        return "test"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Run project tests"

    def add_arguments(self, parser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--report",
            action="store_true",
            help="Show detailed test report including verbose output and coverage",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Run tests in debug mode with verbose output and tracebacks",
        )
        parser.add_argument(
            "args",
            nargs="*",
            help="Additional pytest args (e.g. -k expr)",
        )

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """
        Execute the test command.

        Args:
            *args: Positional arguments (can include pytest arguments like --cov)
            **kwargs: Keyword arguments
        """
        # 显示当前使用的Python环境路径
        python_executable = self.python_detector.get_python_executable()
        print(f"Running tests using Python environment: {python_executable}")

        report_mode = kwargs.get("report", False)
        debug_mode = kwargs.get("debug", False)

        # 处理特殊情况：如果args中有'debug'，将其移除并设置debug_mode为True
        passed_args = kwargs.get("args", [])
        if "debug" in passed_args:
            passed_args.remove("debug")
            debug_mode = True

        print(f"Debug mode: {debug_mode}")
        self._log_report_mode(report_mode)

        # Run pytest to execute tests
        try:
            project_root = self._get_project_root()
            todo_dir = Path(project_root) / "todos"
            todo_dir.mkdir(exist_ok=True)
            self._log_project_paths(project_root, todo_dir)

            cmd_args = self.command_builder.build_command_args(
                report_mode, passed_args, debug_mode
            )

            env = self._build_env(project_root)

            # In all modes, pass through stdout/stderr to preserve colors and formatting
            result = subprocess.run(
                cmd_args,
                cwd=project_root,
                check=False,
                env=env,
            )

            self.result_handler.handle_test_result(result, report_mode)

            if report_mode:
                try:
                    from .test_reporter import generate_reports

                    cov_json = str(todo_dir / "coverage.json")
                    junit_xml = str(todo_dir / "junit.xml")
                    cov_md = str(todo_dir / "coverage.md")
                    err_md = str(todo_dir / "error.md")

                    self._log_report_paths(cov_json, junit_xml)

                    summary = generate_reports(
                        coverage_json_path=cov_json,
                        junit_xml_path=junit_xml,
                        out_cov=cov_md,
                        out_err=err_md,
                        project_root=project_root,
                    )

                    self._log_output_paths(cov_md, err_md)

                    if summary:
                        print(summary)

                    # 添加延迟确保文件完全写入磁盘（Windows系统问题）
                    import time

                    time.sleep(0.5)

                    self._cleanup_temp_files(cov_json, junit_xml)
                except Exception as e:
                    print(f"Failed to generate markdown reports: {e}")
        except FileNotFoundError:
            print(
                "Error: pytest not found. Please install it using 'pip install pytest'"
            )
            sys.exit(1)
        except Exception as e:
            print(f"Error running tests: {e}")
            sys.exit(1)

    def _log_report_mode(self, report_mode: bool) -> None:
        try:
            log_info(f"Report mode: {report_mode}", lang="en")
            log_info(f"报告模式: {report_mode}", lang="zh")
        except Exception:
            pass

    def _log_project_paths(self, project_root: str, todo_dir: Path) -> None:
        try:
            log_info(f"Project root: {project_root}", lang="en")
            log_info(f"Todos dir: {todo_dir}", lang="en")
            log_info(f"项目根目录: {project_root}", lang="zh")
            log_info(f"报告目录: {todo_dir}", lang="zh")
        except Exception:
            pass

    def _build_env(self, project_root: str) -> dict:
        env = os.environ.copy()
        src_path = os.path.join(project_root, "src")
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = src_path
        return env

    def _log_report_paths(self, cov_json: str, junit_xml: str) -> None:
        try:
            log_info(f"Coverage JSON path: {cov_json}", lang="en")
            log_info(f"JUnit XML path: {junit_xml}", lang="en")
            log_info(f"Coverage JSON exists: {Path(cov_json).exists()}", lang="en")
            log_info(f"JUnit XML exists: {Path(junit_xml).exists()}", lang="en")
            log_info(f"覆盖率JSON路径: {cov_json}", lang="zh")
            log_info(f"JUnit XML路径: {junit_xml}", lang="zh")
            log_info(f"覆盖率JSON存在: {Path(cov_json).exists()}", lang="zh")
            log_info(f"JUnit XML存在: {Path(junit_xml).exists()}", lang="zh")
        except Exception:
            pass

    def _log_output_paths(self, cov_md: str, err_md: str) -> None:
        try:
            log_info(f"Coverage MD path: {cov_md}", lang="en")
            log_info(f"Error MD path: {err_md}", lang="en")
            log_info(f"Coverage MD exists: {Path(cov_md).exists()}", lang="en")
            log_info(f"Error MD exists: {Path(err_md).exists()}", lang="en")
            log_info(f"覆盖率Markdown路径: {cov_md}", lang="zh")
            log_info(f"错误Markdown路径: {err_md}", lang="zh")
            log_info(f"覆盖率Markdown存在: {Path(cov_md).exists()}", lang="zh")
            log_info(f"错误Markdown存在: {Path(err_md).exists()}", lang="zh")
        except Exception:
            pass

    def _cleanup_temp_files(self, cov_json: str, junit_xml: str) -> None:
        try:
            if Path(cov_json).exists():
                Path(cov_json).unlink(missing_ok=True)
            if Path(junit_xml).exists():
                Path(junit_xml).unlink(missing_ok=True)
        except Exception:
            pass

    def _get_project_root(self) -> str:
        """
        Get the project root directory.

        Returns:
            str: Path to the project root directory
        """
        try:
            cwd = Path.cwd()
            if (cwd / "tests").exists() or (cwd / "src").exists():
                return str(cwd)
            root = find_project_root()
            return str(root)
        except Exception:
            return os.getcwd()

    # Backward compatibility wrappers for test support
    def _handle_test_result(self, result, report_mode: bool) -> None:
        """Wrapper for backward compatibility with existing tests."""
        return self.result_handler.handle_test_result(result, report_mode)

    def _build_command_args(
        self, report_mode: bool, args, debug_mode: bool = False
    ) -> list[str]:
        """Wrapper for backward compatibility with existing tests."""
        return self.command_builder.build_command_args(report_mode, args, debug_mode)

    def _check_pytest_cov(self) -> bool:
        """Wrapper for backward compatibility with existing tests."""
        return self.command_builder._check_pytest_cov()
