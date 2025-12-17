"""Project root utilities for WL Commands."""

from pathlib import Path
from typing import Optional

from .file_operations import get_file_operations

# Cache for project root paths to avoid repeated filesystem operations
_project_root_cache: dict[str, Path] = {}


def find_project_root(start_path: Path | None = None) -> Path:
    """
    Find the project root directory by looking for pyproject.toml file or .wl directory.

    Args:
        start_path: The path to start searching from. If None, uses current working directory.

    Returns:
        Path: The project root directory path

    Raises:
        FileNotFoundError: If project root with pyproject.toml cannot be found
        OSError: If there are filesystem access issues
    """
    if start_path is None:
        start_path = Path.cwd()

    current_path = start_path.resolve()
    path_str = str(current_path)

    # Check cache first
    if path_str in _project_root_cache:
        return _project_root_cache[path_str]

    file_ops = get_file_operations()

    try:
        # First, check if current directory contains a .wl directory
        if file_ops.exists(current_path / ".wl") and (current_path / ".wl").is_dir():
            _project_root_cache[path_str] = current_path
            return current_path

        # Then check parent directories for pyproject.toml or .wl directory
        check_path = current_path
        while check_path.parent != check_path:
            # Check for pyproject.toml
            marker_file = check_path / "pyproject.toml"
            try:
                if file_ops.exists(marker_file) and marker_file.is_file():
                    # Cache the result
                    _project_root_cache[path_str] = check_path
                    return check_path
            except OSError as e:
                # Handle permission errors or other filesystem issues
                raise OSError(f"无法访问目录 {check_path}: {e}")

            # Check for .wl directory
            wl_dir = check_path / ".wl"
            try:
                if file_ops.exists(wl_dir) and wl_dir.is_dir():
                    # Cache the result
                    _project_root_cache[path_str] = check_path
                    return check_path
            except OSError as e:
                # Handle permission errors or other filesystem issues
                raise OSError(f"无法访问目录 {check_path}: {e}")

            check_path = check_path.parent

        # If we get here, we've reached the filesystem root without finding markers
        # Fall back to current working directory
        _project_root_cache[path_str] = current_path
        return current_path
    except OSError:
        # If we can't access the filesystem, fall back to current directory
        _project_root_cache[path_str] = current_path
        return current_path
    except Exception as e:
        # Handle any other unexpected exceptions by falling back to current directory
        _project_root_cache[path_str] = current_path
        return current_path


def clear_project_root_cache() -> None:
    """Clear the project root cache."""
    _project_root_cache.clear()
