"""
Clean Utils Module
清理工具模块
"""

from py_wlcommands.commands.clean.utils import (
    clean_rust_artifacts as _clean_rust_artifacts,
)
from py_wlcommands.commands.clean.utils import (
    remove_auto_activation_scripts,
    remove_directories,
    remove_egg_info_dirs,
    remove_files,
    remove_log_files,
    remove_pycache_dirs,
    remove_rust_analyzer_dirs,
    remove_uv_lock,
    remove_virtual_environments,
)
from py_wlcommands.utils.logging import log_info

# Keep backward compatibility with tests that import private functions
# 保持与导入私有函数的测试的向后兼容性
_remove_directories = remove_directories
_remove_files = remove_files
_remove_log_files = remove_log_files
_remove_pycache_dirs = remove_pycache_dirs
_remove_egg_info_dirs = remove_egg_info_dirs
_remove_virtual_environments = remove_virtual_environments
_remove_auto_activation_scripts = remove_auto_activation_scripts
_remove_uv_lock = remove_uv_lock


# Public functions
# 公共函数


def clean_build_artifacts() -> None:
    """
    Clean build artifacts and temporary files
    清理构建产物和临时文件
    """
    log_info("Cleaning build artifacts and temporary files...", lang="en")
    log_info("正在清理构建产物和临时文件...", lang="zh")

    # Remove build directories
    build_dirs = [
        "build",
        "dist",
        "results",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "logs",
        "todos",
    ]
    remove_directories(build_dirs)

    # Remove specific files
    files_to_remove = [".coverage"]
    remove_files(files_to_remove)

    # Remove log files
    remove_log_files()

    # Remove pycache directories only in project directory
    remove_pycache_dirs()

    # Remove egg-info directories
    remove_egg_info_dirs()

    # Remove rust-analyzer directories
    remove_rust_analyzer_dirs()

    log_info("Build artifacts and temporary files cleaning completed.", lang="en")
    log_info("构建产物和临时文件清理完成。", lang="zh")


def clean_rust_artifacts() -> None:
    """
    Clean Rust build artifacts
    清理Rust构建产物
    """
    _clean_rust_artifacts()


def clean_all_artifacts() -> None:
    """
    Clean all artifacts including virtual environment
    清理所有产物，包括虚拟环境
    """
    log_info("Cleaning all artifacts...", lang="en")
    log_info("正在清理所有产物...", lang="zh")

    # Clean build artifacts
    clean_build_artifacts()

    # Clean Rust artifacts
    clean_rust_artifacts()

    # Remove virtual environment
    remove_virtual_environments()

    # Remove auto-activation scripts
    remove_auto_activation_scripts()

    # Remove rust-analyzer directories
    remove_rust_analyzer_dirs()

    # Remove uv.lock file
    remove_uv_lock()

    log_info("All artifacts cleaning completed.", lang="en")
    log_info("所有产物清理完成。", lang="zh")


def clean_lfs_artifacts() -> None:
    """
    Clean Git LFS deployment without deleting actual files
    清理Git LFS部署，不删除实际文件
    """
    import os
    import subprocess
    from pathlib import Path

    log_info("Cleaning Git LFS deployment...", lang="en")
    log_info("正在清理Git LFS部署...", lang="zh")

    # 1. Remove Git LFS tracking rules from .gitattributes
    gitattributes_path = Path(".gitattributes")
    if gitattributes_path.exists():
        log_info("Removing Git LFS tracking rules from .gitattributes...", lang="en")
        log_info("正在从.gitattributes中移除Git LFS跟踪规则...", lang="zh")

        # Read the current content
        with open(gitattributes_path) as f:
            lines = f.readlines()

        # Filter out Git LFS tracking rules
        filtered_lines = []
        for line in lines:
            # Check if the line contains Git LFS tracking rules
            if (
                "filter=lfs" not in line
                and "diff=lfs" not in line
                and "merge=lfs" not in line
            ):
                filtered_lines.append(line)

        # Write back the filtered content
        with open(gitattributes_path, "w") as f:
            f.writelines(filtered_lines)

        log_info("✓ Removed Git LFS tracking rules from .gitattributes", lang="en")
        log_info("✓ 已从.gitattributes中移除Git LFS跟踪规则", lang="zh")

    # 2. Run git lfs uninstall to remove Git LFS hooks
    log_info("Removing Git LFS hooks...", lang="en")
    log_info("正在移除Git LFS钩子...", lang="zh")

    try:
        result = subprocess.run(
            ["git", "lfs", "uninstall"], check=True, capture_output=True, text=True
        )

        # Filter out warning messages from the output
        stdout_lines = result.stdout.strip().split("\n")
        filtered_lines = [
            line for line in stdout_lines if not line.startswith("warning:")
        ]
        filtered_output = "\n".join(filtered_lines).strip()

        # Only log if there's meaningful output, otherwise just confirm success
        if filtered_output:
            log_info(f"✓ Git LFS hooks removed: {filtered_output}", lang="en")
            log_info(f"✓ Git LFS钩子已移除: {filtered_output}", lang="zh")
        else:
            log_info("✓ Git LFS hooks removed", lang="en")
            log_info("✓ Git LFS钩子已移除", lang="zh")
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.strip() if e.stderr else "Unknown error"
        log_info(f"✗ Failed to remove Git LFS hooks: {stderr_msg}", lang="en")
        log_info(f"✗ 移除Git LFS钩子失败: {stderr_msg}", lang="zh")

    log_info("Git LFS deployment cleaning completed.", lang="en")
    log_info("Git LFS部署清理完成。", lang="zh")
