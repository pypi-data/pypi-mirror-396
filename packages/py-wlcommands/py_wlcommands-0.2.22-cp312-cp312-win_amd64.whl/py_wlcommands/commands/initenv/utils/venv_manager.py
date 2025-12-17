"""Virtual environment manager utility."""

import subprocess
import sys

from ....utils.logging import log_info
from .log_manager import performance_monitor


class VenvManager:
    """Virtual environment manager."""

    def __init__(self, env: dict[str, str]) -> None:
        self.env = env

    @performance_monitor
    def create_venv_windows(self, venv_path: str, python_version: str) -> bool:
        """Create virtual environment on Windows."""
        try:
            # Try using uv module first
            cmd = [sys.executable, "-m", "uv", "venv", venv_path]

            result = subprocess.run(
                cmd, capture_output=True, text=True, env=self.env, encoding="utf-8"
            )

            # If module not found, try using uv command directly
            if result.returncode != 0 and "No module named uv" in result.stderr:
                log_info("uv module not found, trying uv command directly...")
                cmd = ["uv", "venv", venv_path]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, env=self.env, encoding="utf-8"
                )

            if result.returncode == 0:
                log_info(f"✓ Virtual environment created at {venv_path}")
                log_info(f"✓ 虚拟环境已在 {venv_path} 创建", lang="zh")
                return True
            else:
                log_info(
                    f"Warning: Failed to create virtual environment: {result.stderr}"
                )
                log_info(f"警告: 创建虚拟环境失败: {result.stderr}", lang="zh")
                return False
        except Exception as e:
            log_info(f"Warning: Failed to create virtual environment: {e}")
            log_info(f"警告: 创建虚拟环境失败: {e}", lang="zh")
            return False

    @performance_monitor
    def create_venv_unix(
        self, venv_path: str, python_version: str, env: dict[str, str]
    ) -> bool:
        """Create virtual environment on Unix-like systems."""
        try:
            # Use uv to create virtual environment
            cmd = ["uv", "venv", venv_path]

            result = subprocess.run(
                cmd, capture_output=True, text=True, env=env, encoding="utf-8"
            )

            if result.returncode == 0:
                log_info(f"✓ Virtual environment created at {venv_path}")
                log_info(f"✓ 虚拟环境已在 {venv_path} 创建", lang="zh")
                return True
            else:
                log_info(
                    f"Warning: Failed to create virtual environment: {result.stderr}"
                )
                log_info(f"警告: 创建虚拟环境失败: {result.stderr}", lang="zh")
                return False
        except Exception as e:
            log_info(f"Warning: Failed to create virtual environment: {e}")
            log_info(f"警告: 创建虚拟环境失败: {e}", lang="zh")
            return False

    @performance_monitor
    def sync_environment(self, venv_path: str = ".venv") -> bool:
        """Sync the environment by updating dependencies."""
        log_info("Syncing environment dependencies...")
        log_info("同步环境依赖...", lang="zh")

        try:
            # 更新依赖
            log_info("Updating dependencies with uv...")
            log_info("使用uv更新依赖...", lang="zh")
            cmd = ["uv", "sync"]

            result = subprocess.run(
                cmd, capture_output=True, text=True, env=self.env, encoding="utf-8"
            )

            if result.returncode == 0:
                log_info("✓ Dependencies updated successfully")
                log_info("✓ 依赖更新成功", lang="zh")
                return True
            else:
                log_info(f"Warning: Failed to update dependencies: {result.stderr}")
                log_info(f"警告: 更新依赖失败: {result.stderr}", lang="zh")
                return False
        except Exception as e:
            log_info(f"Warning: Failed to sync environment: {e}")
            log_info(f"警告: 同步环境失败: {e}", lang="zh")
            return False
