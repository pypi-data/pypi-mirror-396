"""
Directory walking utilities for deployment functionality.
"""

import os

from .directory_utils import is_excluded_file, is_ignored_directory, is_in_whitelist
from .symlink_manager import create_symlink


def _process_files_in_directory(
    root: str,
    source_dir: str,
    py_dir: str,
    rel_path: str,
    dirs: list[str],
    files: list[str],
) -> bool:
    """
    处理目录中的文件和子目录，创建软链接
    """
    success = True

    # 处理当前目录中的文件
    for file in files:
        source_file = os.path.join(root, file)

        # 检查是否在白名单中
        if not is_in_whitelist(source_file, source_dir):
            continue

        # 排除特定文件
        if rel_path == "" and is_excluded_file(file):
            continue

        # 排除任何目录下的.gitignore文件
        if file == ".gitignore":
            continue

        target_file = os.path.join(py_dir, rel_path, file)

        if not create_symlink(source_file, target_file):
            success = False

    # 处理当前目录中的子目录
    for dir_name in dirs:
        source_dir_path = os.path.join(root, dir_name)

        # 检查是否在白名单中
        if not is_in_whitelist(source_dir_path, source_dir):
            continue

        target_dir_path = os.path.join(py_dir, rel_path, dir_name)

        # 只为空目录创建链接
        try:
            if not os.listdir(source_dir_path):
                if not create_symlink(source_dir_path, target_dir_path):
                    success = False
        except OSError:
            success = False

    return success


def _walk_source_directory(source_dir: str, py_dir: str) -> bool:
    """
    遍历源目录，为指定的py目录创建软链接
    """
    success = True

    # 遍历源目录中的所有内容
    try:
        for root, dirs, files in os.walk(source_dir):
            # 忽略特定目录
            dirs[:] = [d for d in dirs if not is_ignored_directory(d)]

            # 计算相对路径
            rel_path = os.path.relpath(root, source_dir)
            if rel_path == ".":
                rel_path = ""

            if not _process_files_in_directory(
                root, source_dir, py_dir, rel_path, dirs, files
            ):
                success = False
    except OSError:
        success = False

    return success
