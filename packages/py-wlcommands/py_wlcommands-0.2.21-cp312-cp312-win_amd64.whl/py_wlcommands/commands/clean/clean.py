"""
Command to clean project build artifacts.
"""

import sys

from py_wlcommands.commands import Command, register_command, validate_command_args
from py_wlcommands.utils.logging import log_info

from .clean_utils import (
    clean_all_artifacts,
    clean_build_artifacts,
    clean_lfs_artifacts,
    clean_rust_artifacts,
)


@register_command("clean")
class CleanCommand(Command):
    """Command to clean project build artifacts."""

    @property
    def name(self) -> str:
        return "clean"

    @property
    def help(self) -> str:
        return "Clean project build artifacts"

    @classmethod
    def add_arguments(cls, parser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "target",
            nargs="?",
            default="build",
            choices=["build", "all", "rust", "lfs"],
            help="Target to clean (build, all, rust, lfs)",
        )

    @validate_command_args()
    def execute(self, target: str = "build") -> None:
        """
        Clean project - equivalent to make clean
        清理项目 - 等效于 make clean
        """
        # Use simple logging instead of structured logging for user-facing messages
        if target == "all":
            log_info("Cleaning all project artifacts including virtual environment...")
            log_info("正在清理所有项目产物，包括虚拟环境...", lang="zh")
        elif target == "rust":
            log_info("Cleaning Rust build artifacts...")
            log_info("正在清理Rust构建产物...", lang="zh")
        elif target == "lfs":
            log_info("Cleaning Git LFS deployment...")
            log_info("正在清理Git LFS部署...", lang="zh")
        else:
            log_info("Cleaning project build artifacts...")
            log_info("正在清理项目构建产物...", lang="zh")

        try:
            # Clean based on target
            # 根据目标清理
            if target == "all":
                clean_all_artifacts()
            elif target == "rust":
                clean_rust_artifacts()  # 使用clean_utils中定义的函数
            elif target == "lfs":
                clean_lfs_artifacts()  # 使用clean_utils中定义的函数
            else:
                clean_build_artifacts()

            # Use simple logging for user-facing messages
            if target == "all":
                log_info("Complete project cleaning completed successfully!")
                log_info("完整项目清理成功完成！", lang="zh")
            elif target == "rust":
                log_info("Rust cleaning completed successfully!")
                log_info("Rust清理成功完成！", lang="zh")
            elif target == "lfs":
                log_info("Git LFS cleaning completed successfully!")
                log_info("Git LFS清理成功完成！", lang="zh")
            else:
                log_info("Project cleaning completed successfully!")
                log_info("项目清理成功完成！", lang="zh")
        except Exception as e:
            log_info(f"Error cleaning project: {e}", lang="en")
            log_info(f"错误：清理项目失败: {e}", lang="zh")
            sys.exit(1)
