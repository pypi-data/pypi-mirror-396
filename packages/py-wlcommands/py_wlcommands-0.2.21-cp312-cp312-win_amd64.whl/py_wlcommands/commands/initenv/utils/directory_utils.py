"""
Directory utilities for deployment functionality.
"""

import os

from .deploy_config import DEPLOY_WHITELIST


def find_py_directories() -> list[str]:
    """
    查找当前目录下所有以 py_ 开头的文件夹
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    py_dirs = []

    try:
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if item.startswith("py_") and os.path.isdir(item_path):
                py_dirs.append(item_path)
    except OSError:
        pass

    return py_dirs


def is_ignored_directory(dir_name: str) -> bool:
    """
    检查目录是否应被忽略
    """
    ignored_dirs = [".git", "__pycache__"]  # 移除了 .cursor 和 .uv
    for ignored in ignored_dirs:
        if ignored in dir_name.split(os.sep):
            return True
    return False


def is_excluded_file(file_name: str) -> bool:
    """
    检查文件是否应被排除不创建链接
    """
    excluded_files = ["README.md", ".gitignore"]  # 添加.gitignore到排除列表
    return file_name in excluded_files


def is_in_whitelist(path: str, source_dir: str) -> bool:
    """
    检查文件或目录是否在白名单中
    """
    try:
        rel_path = os.path.relpath(path, source_dir)
        if rel_path == ".":
            return False

        # 检查路径或其父目录是否在白名单中
        path_parts = rel_path.split(os.sep)
        for i in range(len(path_parts)):
            if os.sep.join(path_parts[: i + 1]) in DEPLOY_WHITELIST:
                return True
        return False
    except (OSError, ValueError):
        return False
