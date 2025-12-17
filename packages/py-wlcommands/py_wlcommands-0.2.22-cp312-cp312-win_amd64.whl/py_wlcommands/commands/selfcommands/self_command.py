"""
Self update command.
"""

import argparse

from .. import Command, register_command, validate_command_args
from ..self import shutil, subprocess, sys
from .installation_manager import InstallationManager
from .local_installer import LocalInstaller
from .pypi_updater import PypiUpdater
from .windows_update import WindowsUpdate


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
        parser.add_argument(
            "path",
            nargs="?",
            default=None,
            help="Path to local source (default: None, which means update from PyPI)",
        )

    @validate_command_args(subcommand=lambda x: x in [None, "update"])
    def execute(self, subcommand: str = "update", path: str = None) -> None:
        """
        Self update the wl command with reinstall logic.
        自我更新wl命令，包含重新安装逻辑。

        Args:
            subcommand (str): The subcommand to execute. Defaults to "update".
            path (str): Path to local source (default: None, which means update from PyPI)
        """
        from py_wlcommands.utils.logging import log_info

        # Use simple logging instead of structured logging for user-facing messages
        log_info("Updating wl command...")
        log_info("正在更新wl命令...", lang="zh")

        # Initialize variables that need to be accessible in except blocks
        uv_path = None
        timeout_duration = 300  # 5 minutes timeout

        try:
            # Initialize managers
            installation_manager = InstallationManager()
            uv_path, env = installation_manager.prepare_environment()

            # Determine whether to install local or update from PyPI
            if path is not None and path == ".":
                # Install local code (like reinstall.bat)
                local_installer = LocalInstaller()
                local_installer.install(uv_path, env)
            else:
                # Update from PyPI using the same installation method
                pypi_updater = PypiUpdater()
                pypi_updater.update(uv_path, env)
        except Exception as e:
            # Check if this is a Windows permission error
            if sys.platform.startswith(
                "win"
            ) and installation_manager.is_file_in_use_error(str(e)):
                windows_update = WindowsUpdate()
                windows_update.handle_access_error(uv_path)
            else:
                log_info(f"Error updating wl command: {e}", lang="en")
                log_info(f"错误：更新wl命令失败: {e}", lang="zh")
                sys.exit(1)

    # Wrapper methods for backward compatibility with tests
    def _run_delayed_update(self, uv_path: str, env: dict) -> None:
        """Wrapper for _run_delayed_update to maintain backward compatibility."""
        windows_update = WindowsUpdate()
        windows_update._run_delayed_update(uv_path, env)

    def _show_manual_instructions(self) -> None:
        """Wrapper for _show_manual_instructions to maintain backward compatibility."""
        windows_update = WindowsUpdate()
        windows_update._show_manual_instructions()
