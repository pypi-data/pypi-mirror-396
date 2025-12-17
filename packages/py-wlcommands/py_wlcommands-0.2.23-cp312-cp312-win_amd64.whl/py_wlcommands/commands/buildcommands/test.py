"""
Test command for WL Commands.
"""

import subprocess
import sys
from typing import Any

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info
from ...utils.subprocess import run_command
from .. import Command, register_command


@register_command("build test")
class BuildTestCommand(Command):
    """Command to build test environment and run unit tests."""

    @property
    def name(self) -> str:
        """Return the command name."""
        return "test"

    @property
    def help(self) -> str:
        """Return the command help text."""
        return "Build test environment and run unit tests"

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Execute the build test command."""
        # Run tests using Python's unittest module directly
        try:
            log_info("Building test environment and running tests...")
            log_info("构建测试环境并运行测试...", lang="zh")

            # Run tests using python -m unittest discover
            run_command(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                capture_output=False,
            )

            log_info("✓ Tests completed successfully")
            log_info("✓ 测试成功完成", lang="zh")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to run tests: {e}")
            log_error(f"运行测试失败: {e}", lang="zh")
            raise CommandError(f"Test failed with return code {e.returncode}")
        except FileNotFoundError:
            log_error("Python interpreter not found.")
            log_error("未找到Python解释器。", lang="zh")
            raise CommandError("Python interpreter not found")
        except Exception as e:
            log_error(f"Unexpected error during test execution: {e}")
            log_error(f"测试执行过程中出现意外错误: {e}", lang="zh")
            raise CommandError(f"Test failed: {e}")
