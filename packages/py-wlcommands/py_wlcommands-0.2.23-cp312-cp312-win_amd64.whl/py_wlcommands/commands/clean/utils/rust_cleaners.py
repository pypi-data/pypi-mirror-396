"""
Rust-specific cleaning utilities for clean command.
"""

import os
import shutil

from py_wlcommands.utils.logging import log_info


def remove_rust_analyzer_dirs() -> None:
    """Remove rust-analyzer directories."""
    rust_analyzer_dirs = ["target/rust-analyzer", "rust/target/rust-analyzer"]
    for dir_path in rust_analyzer_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                log_info(f"Removed rust-analyzer directory: {dir_path}", lang="en")
                log_info(f"已删除rust-analyzer目录: {dir_path}", lang="zh")
            except Exception as e:
                log_info(
                    f"Failed to remove rust-analyzer directory {dir_path}: {e}",
                    lang="en",
                )
                log_info(f"删除rust-analyzer目录 {dir_path} 失败: {e}", lang="zh")


def clean_rust_artifacts() -> None:
    """
    Clean Rust build artifacts
    清理Rust构建产物
    """
    # Check if Rust is enabled and directory exists
    rust_dir = "rust"
    if os.path.exists(rust_dir):
        rust_target_dir = os.path.join(rust_dir, "target")
        if os.path.exists(rust_target_dir):
            try:
                shutil.rmtree(rust_target_dir)
                log_info(f"Removed Rust target directory: {rust_target_dir}", lang="en")
                log_info(f"已删除Rust target目录: {rust_target_dir}", lang="zh")
            except Exception as e:
                log_info(
                    f"Failed to remove Rust target directory {rust_target_dir}: {e}",
                    lang="en",
                )
                log_info(f"删除Rust target目录 {rust_target_dir} 失败: {e}", lang="zh")
        else:
            log_info("Rust target directory does not exist, skipping...", lang="en")
            log_info("Rust target目录不存在，跳过...", lang="zh")
    else:
        log_info("Rust directory does not exist, skipping...", lang="en")
        log_info("Rust目录不存在，跳过...", lang="zh")

    # Remove rust-analyzer directory in root target
    root_rust_analyzer_dir = "target/rust-analyzer"
    if os.path.exists(root_rust_analyzer_dir):
        try:
            shutil.rmtree(root_rust_analyzer_dir)
            log_info(
                f"Removed root rust-analyzer directory: {root_rust_analyzer_dir}",
                lang="en",
            )
            log_info(
                f"已删除根目录rust-analyzer目录: {root_rust_analyzer_dir}", lang="zh"
            )
        except Exception as e:
            log_info(
                f"Failed to remove root rust-analyzer directory {root_rust_analyzer_dir}: {e}",
                lang="en",
            )
            log_info(
                f"删除根目录rust-analyzer目录 {root_rust_analyzer_dir} 失败: {e}",
                lang="zh",
            )
