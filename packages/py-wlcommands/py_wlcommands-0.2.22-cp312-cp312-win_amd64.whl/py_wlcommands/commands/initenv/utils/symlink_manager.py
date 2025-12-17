"""
Symlink management utilities for deployment.
"""

import os
import platform
import shutil


def create_symlink(source: str, target: str) -> bool:
    """
    创建从源到目标的软链接，处理平台差异
    """
    source = os.path.abspath(source)
    target = os.path.abspath(target)

    # 如果目标文件已存在，先删除
    if os.path.exists(target):
        try:
            if os.path.islink(target):
                os.unlink(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            elif os.path.isfile(target):
                os.remove(target)
        except OSError:
            return False

    # 确保目标目录存在
    target_dir = os.path.dirname(target)
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError:
        return False

    # 创建软链接（处理不同操作系统）
    try:
        if platform.system() == "Windows":
            # Windows 需要管理员权限并区分目录和文件链接
            is_directory = os.path.isdir(source)
            if is_directory:
                # Windows 10以上版本支持目录符号链接，低版本需使用junction
                os.symlink(source, target, target_is_directory=True)
            else:
                os.symlink(source, target)
        else:
            # Unix/Linux/macOS
            os.symlink(source, target)
        return True
    except OSError:
        return False
