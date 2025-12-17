"""
Symlink cleaning utilities for deployment functionality.
"""

import os


def _clean_file_symlinks(root: str, files: list[str], source_dir_basename: str) -> int:
    """
    清理文件软链接

    Args:
        root: 根目录路径
        files: 文件列表
        source_dir_basename: 源目录基本名称

    Returns:
        int: 清理的链接数量
    """
    cleaned_count = 0
    for file in files:
        file_path = os.path.join(root, file)
        if os.path.islink(file_path):
            try:
                link_target = os.readlink(file_path)
                if source_dir_basename in link_target:
                    os.unlink(file_path)
                    cleaned_count += 1
            except OSError:
                pass
    return cleaned_count


def _clean_directory_symlinks(
    root: str, dirs: list[str], source_dir_basename: str
) -> tuple[int, list[str]]:
    """
    清理目录软链接

    Args:
        root: 根目录路径
        dirs: 目录列表
        source_dir_basename: 源目录基本名称

    Returns:
        tuple[int, list[str]]: (清理的链接数量, 需要从遍历中移除的目录列表)
    """
    cleaned_count = 0
    removed_dirs = []
    for dir_name in dirs[:]:  # 使用副本进行迭代，因为我们可能会修改dirs
        dir_path = os.path.join(root, dir_name)
        if os.path.islink(dir_path):
            try:
                link_target = os.readlink(dir_path)
                if source_dir_basename in link_target:
                    os.unlink(dir_path)
                    cleaned_count += 1
                    removed_dirs.append(dir_name)  # 记录需要移除的目录
            except OSError:
                pass
    return cleaned_count, removed_dirs


def clean_existing_symlinks(
    py_dirs: list[str], source_dir_name: str = "shared-build-system"
) -> int:
    """
    清理目标文件夹中已有的软链接
    """
    cleaned_count = 0
    source_dir_basename = os.path.basename(source_dir_name)

    for py_dir in py_dirs:
        if not os.path.exists(py_dir):
            continue

        # 递归清理子目录中的链接
        try:
            for root, dirs, files in os.walk(py_dir):
                # 清理文件链接
                cleaned_count += _clean_file_symlinks(root, files, source_dir_basename)

                # 清理目录链接
                dir_cleaned_count, removed_dirs = _clean_directory_symlinks(
                    root, dirs, source_dir_basename
                )
                cleaned_count += dir_cleaned_count

                # 从遍历列表中移除已清理的目录
                for removed_dir in removed_dirs:
                    try:
                        dirs.remove(removed_dir)
                    except ValueError:
                        pass  # 目录不在列表中，忽略

        except OSError:
            pass

    return cleaned_count
