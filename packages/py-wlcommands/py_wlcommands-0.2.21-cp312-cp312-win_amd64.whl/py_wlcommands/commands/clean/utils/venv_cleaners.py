"""
Virtual environment cleaning utilities for clean command.
"""

import os
import shutil

from py_wlcommands.utils.logging import log_info


def remove_virtual_environments() -> None:
    """
    Remove virtual environments
    删除虚拟环境
    """
    venv_dirs = [".venv", "venv"]
    for venv_dir in venv_dirs:
        if os.path.exists(venv_dir):
            try:
                shutil.rmtree(venv_dir)
                log_info(
                    f"Removed virtual environment directory: {venv_dir}", lang="en"
                )
                log_info(f"已删除虚拟环境目录: {venv_dir}", lang="zh")
            except Exception as e:
                log_info(
                    f"Failed to remove virtual environment {venv_dir}: {e}", lang="en"
                )
                log_info(f"删除虚拟环境 {venv_dir} 失败: {e}", lang="zh")
        else:
            log_info(
                f"Virtual environment directory {venv_dir} does not exist, skipping...",
                lang="en",
            )
            log_info(f"虚拟环境目录 {venv_dir} 不存在，跳过...", lang="zh")


def remove_auto_activation_scripts() -> None:
    """
    Remove auto-activation scripts
    删除自动激活脚本
    """
    auto_activate_scripts = ["auto_activate_venv.bat", "auto_activate_venv.sh"]
    for script in auto_activate_scripts:
        if os.path.exists(script):
            try:
                os.remove(script)
                log_info(f"Removed auto-activation script: {script}", lang="en")
                log_info(f"已删除自动激活脚本: {script}", lang="zh")
            except Exception as e:
                log_info(
                    f"Failed to remove auto-activation script {script}: {e}", lang="en"
                )
                log_info(f"删除自动激活脚本 {script} 失败: {e}", lang="zh")


def remove_uv_lock() -> None:
    """
    Remove uv.lock file
    删除uv.lock文件
    """
    uv_lock_file = "uv.lock"
    if os.path.exists(uv_lock_file):
        try:
            os.remove(uv_lock_file)
            log_info(f"Removed {uv_lock_file} file", lang="en")
            log_info(f"已删除 {uv_lock_file} 文件", lang="zh")
        except Exception as e:
            log_info(f"Failed to remove {uv_lock_file} file: {e}", lang="en")
            log_info(f"删除 {uv_lock_file} 文件失败: {e}", lang="zh")
