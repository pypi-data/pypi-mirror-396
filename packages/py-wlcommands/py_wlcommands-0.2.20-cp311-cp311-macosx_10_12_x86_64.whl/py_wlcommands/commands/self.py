"""
Self update command.
"""

import argparse
import os
import shutil
import subprocess
import sys

from . import Command, register_command, validate_command_args


@register_command("self")
class SelfCommand(Command):
    """Command for self-management of the wl command."""

    @property
    def name(self) -> str:
        return "self"

    @property
    def help(self) -> str:
        return "Self management commands"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add arguments to the parser."""
        parser.add_argument(
            "subcommand",
            nargs="?",
            default="update",
            choices=["update"],
            help="Subcommand to execute (default: update)",
        )

    @validate_command_args(subcommand=lambda x: x in [None, "update"])
    def execute(self, subcommand: str = "update") -> None:
        """
        Self update the wl command - equivalent to uv tool install --editable .
        自我更新wl命令 - 等效于 uv tool install --editable .

        Args:
            subcommand (str): The subcommand to execute. Defaults to "update".
        """
        from ..utils.logging import log_info

        # Use simple logging instead of structured logging for user-facing messages
        log_info("Updating wl command...")
        log_info("正在更新wl命令...", lang="zh")

        try:
            # Prepare environment variables
            env = os.environ.copy()

            # Fix encoding issues on Windows
            if sys.platform.startswith("win"):
                # Set environment variables to ensure proper UTF-8 handling
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONLEGACYWINDOWSFSENCODING"] = "1"

            # Find uv executable path to avoid Ruff(S607) error
            uv_path = shutil.which("uv")
            if uv_path is None:
                raise FileNotFoundError("uv command not found in PATH")

            # Run uv tool install --editable . command
            # 执行 uv tool install --editable . 命令
            subprocess.run(
                [uv_path, "tool", "install", "--editable", "."],
                check=True,
                capture_output=False,
                text=True,
                # Explicitly set encoding for Windows systems
                encoding="utf-8" if sys.platform.startswith("win") else None,
                env=env,
            )
            log_info("WL command updated successfully!")
            log_info("wl命令更新成功！", lang="zh")
        except subprocess.CalledProcessError as e:
            # Check if this is a Windows permission error
            if sys.platform.startswith("win") and "Access is denied" in str(e):
                log_info(
                    "Error updating wl command: Access denied. This is a common issue on Windows when trying to update a running tool.",
                    lang="en",
                )
                log_info(
                    "错误：更新wl命令失败: 权限被拒绝。这是在Windows上尝试更新正在运行的工具时的常见问题。",
                    lang="zh",
                )
                log_info("Please try one of the following solutions:", lang="en")
                log_info("请尝试以下解决方案之一：", lang="zh")
                log_info(
                    "1. Close all wl command windows and run 'wl self update' again",
                    lang="en",
                )
                log_info(
                    "   关闭所有wl命令窗口，然后再次运行'wl self update'", lang="zh"
                )
                log_info("2. Run the command as administrator", lang="en")
                log_info("   以管理员身份运行命令", lang="zh")
                log_info("3. Use 'uv tool install --editable .' directly", lang="en")
                log_info("   直接使用'uv tool install --editable .'命令", lang="zh")
            else:
                log_info(f"Error updating wl command: {e}", lang="en")
                log_info(f"错误：更新wl命令失败: {e}", lang="zh")
            sys.exit(1)
        except FileNotFoundError:
            log_info(
                "Error: 'uv' command not found. Please ensure it is installed and in PATH.",
                lang="en",
            )
            log_info("错误：未找到'uv'命令。请确保已安装并添加到PATH中。", lang="zh")
            sys.exit(1)
