"""
Python-specific cleaning utilities for clean command.
"""

import glob
import os
import shutil
from pathlib import Path

from py_wlcommands.utils.logging import log_info


def remove_log_files() -> None:
    """Remove log files."""
    try:
        for log_file in glob.glob("*.log"):
            os.remove(log_file)
            log_info(f"Removed log file: {log_file}", lang="en")
            log_info(f"已删除日志文件: {log_file}", lang="zh")
    except Exception as e:
        log_info(f"Failed to remove log files: {e}", lang="en")
        log_info(f"删除日志文件失败: {e}", lang="zh")


def remove_pycache_dirs() -> None:
    """Remove __pycache__ directories only in project directory (not in venv)."""
    try:
        project_root = Path(".").resolve()
        for pycache_dir in project_root.rglob("__pycache__"):
            # Skip pycache directories in virtual environments
            if ".venv" in str(pycache_dir) or "venv" in str(pycache_dir):
                continue

            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                log_info(f"Removed pycache directory: {pycache_dir}", lang="en")
                log_info(f"已删除pycache目录: {pycache_dir}", lang="zh")
    except Exception as e:
        log_info(f"Failed to remove pycache directories: {e}", lang="en")
        log_info(f"删除pycache目录失败: {e}", lang="zh")


def remove_egg_info_dirs() -> None:
    """Remove egg-info directories only in project directory."""
    try:
        project_root = Path(".").resolve()
        for egg_info_dir in project_root.rglob("*.egg-info"):
            # Skip egg-info directories in virtual environments
            if ".venv" in str(egg_info_dir) or "venv" in str(egg_info_dir):
                continue

            if egg_info_dir.is_dir():
                shutil.rmtree(egg_info_dir)
                log_info(f"Removed egg-info directory: {egg_info_dir}", lang="en")
                log_info(f"已删除egg-info目录: {egg_info_dir}", lang="zh")
    except Exception as e:
        log_info(f"Failed to remove egg-info directories: {e}", lang="en")
        log_info(f"删除egg-info目录失败: {e}", lang="zh")


def clean_build_artifacts() -> None:
    """Clean build artifacts like build, dist, .coverage, etc."""
    try:
        # Remove build, dist, and results directories
        from py_wlcommands.commands.clean.utils.core_cleaners import remove_directories

        remove_directories(["build", "dist", "results"])

        # Remove .coverage file
        from py_wlcommands.commands.clean.utils.core_cleaners import remove_files

        remove_files([".coverage"])

        # Remove log files
        remove_log_files()

        # Remove __pycache__ directories
        remove_pycache_dirs()

        # Remove egg-info directories
        remove_egg_info_dirs()
    except Exception as e:
        log_info(f"Failed to clean build artifacts: {e}", lang="en")
        log_info(f"清理构建产物失败: {e}", lang="zh")
