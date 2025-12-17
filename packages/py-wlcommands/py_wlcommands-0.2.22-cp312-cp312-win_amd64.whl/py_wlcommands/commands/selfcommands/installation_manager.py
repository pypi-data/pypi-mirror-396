"""
Installation manager for self update command.
"""

import os


class InstallationManager:
    """Manager for handling installation-related functionality."""

    def prepare_environment(self) -> tuple[str, dict]:
        """
        Prepare environment variables and find uv executable.
        """
        from py_wlcommands.utils.logging import log_info

        from ..self import shutil, sys

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

        return uv_path, env

    def uninstall_existing(self, uv_path: str, env: dict) -> None:
        """
        Uninstall existing py_wlcommands (ignore failure if not installed).
        """
        from py_wlcommands.utils.logging import log_info

        from ..self import subprocess, sys

        log_info("Uninstalling existing py_wlcommands...")
        log_info("正在卸载现有py_wlcommands...", lang="zh")

        # Run uninstall command (ignore failure if not installed)
        uninstall_result = subprocess.run(
            [uv_path, "tool", "uninstall", "py_wlcommands"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8" if sys.platform.startswith("win") else None,
            env=env,
        )

        if uninstall_result.returncode != 0:
            log_info(
                "Note: py_wlcommands was not installed or failed to uninstall. Continuing with installation."
            )
            log_info("注意：py_wlcommands未安装或卸载失败。继续安装。", lang="zh")
        else:
            log_info("Successfully uninstalled existing py_wlcommands.")
            log_info("成功卸载现有py_wlcommands。", lang="zh")

    def is_file_in_use_error(self, error_msg: str) -> bool:
        """
        Check if the error message indicates a file in use error on Windows.
        """
        return any(
            keyword in error_msg
            for keyword in [
                "Access is denied",
                "无法访问文件",
                "The process cannot access the file",
            ]
        )

    def detect_installation_method(self) -> str:
        """
        Detect how the current wl command is installed.

        Returns:
            str: Installation method - "uv_tool", "uv_pip", "pip", or "unknown"
        """
        from py_wlcommands.utils.logging import log_info

        # Check if running in uv tool environment
        if "UV_TOOL_DIR" in os.environ or "UV_PYTHON" in os.environ:
            log_info("Detected installation method: uv tool")
            log_info("检测到安装方式: uv tool", lang="zh")
            return "uv_tool"

        # Check if uv is used for pip
        try:
            import importlib.metadata

            dist = importlib.metadata.distribution("py_wlcommands")
            log_info(f"Detected distribution: {dist}")
            log_info(f"检测到发行版: {dist}", lang="zh")

            # This is a simplified check - in real scenario we might need more robust detection
            # For now, we'll assume that if we're not in uv tool, it's either uv pip or regular pip
            log_info("Detected installation method: uv pip")
            log_info("检测到安装方式: uv pip", lang="zh")
            return "uv_pip"
        except (
            importlib.metadata.PackageNotFoundError,
            importlib.metadata.Error,
            Exception,
        ) as e:
            log_info(f"Warning: Could not detect installation method: {e}")
            log_info(f"警告: 无法检测安装方式: {e}", lang="zh")
            return "unknown"
