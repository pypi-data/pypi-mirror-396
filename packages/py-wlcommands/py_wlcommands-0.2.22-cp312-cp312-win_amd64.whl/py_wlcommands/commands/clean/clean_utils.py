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
    import shutil
    import subprocess
    from pathlib import Path

    log_info("Cleaning Git LFS deployment...", lang="en")
    log_info("正在清理Git LFS部署...", lang="zh")

    # 检查并移除嵌套的.git目录
    _handle_nested_git_dirs()

    # 清理.gitattributes文件中的LFS跟踪规则
    _clean_gitattributes()

    # 卸载Git LFS钩子
    _uninstall_git_lfs()

    log_info("Git LFS deployment cleaning completed.", lang="en")
    log_info("Git LFS部署清理完成。", lang="zh")


def _find_nested_git_dirs() -> list:
    """查找嵌套的.git目录（不包括根目录的.git）"""
    from pathlib import Path

    current_dir = Path.cwd()
    nested_git_dirs = []

    for git_dir in current_dir.glob("**/.git"):
        # 跳过根目录的.git文件夹
        if git_dir.parent == current_dir:
            continue
        # 检查是否是目录
        if git_dir.is_dir():
            nested_git_dirs.append(git_dir)

    return nested_git_dirs


def _remove_nested_git_dirs(nested_git_dirs: list) -> None:
    """移除嵌套的.git目录"""
    import shutil

    log_info("\nAutomatically removing nested .git directories...", lang="en")
    log_info("\n正在自动移除嵌套的.git目录...", lang="zh")

    for git_dir in nested_git_dirs:
        try:
            shutil.rmtree(git_dir)
            log_info(f"✓ Successfully removed: {git_dir}", lang="en")
            log_info(f"✓ 成功移除: {git_dir}", lang="zh")
        except Exception as e:
            log_info(f"✗ Failed to remove {git_dir}: {e}", lang="en")
            log_info(f"✗ 移除失败 {git_dir}: {e}", lang="zh")


def _handle_nested_git_dirs() -> None:
    """处理嵌套的.git目录"""
    log_info("Checking for nested .git directories...", lang="en")
    log_info("正在检查嵌套的.git目录...", lang="zh")

    nested_git_dirs = _find_nested_git_dirs()

    if nested_git_dirs:
        log_info(
            "Found nested .git directories, removing them to fix Git operations:",
            lang="en",
        )
        log_info("发现嵌套的.git目录，正在移除它们以修复Git操作：", lang="zh")

        for git_dir in nested_git_dirs:
            log_info(f"  - {git_dir}", lang="en")
            log_info(f"  - {git_dir}", lang="zh")

        _remove_nested_git_dirs(nested_git_dirs)
    else:
        log_info("✓ No nested .git directories found", lang="en")
        log_info("✓ 未发现嵌套的.git目录", lang="zh")


def _clean_gitattributes() -> None:
    """清理.gitattributes文件中的LFS跟踪规则"""
    from pathlib import Path

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


def _uninstall_git_lfs() -> None:
    """卸载Git LFS钩子"""
    import subprocess

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
