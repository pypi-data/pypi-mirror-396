"""File operations utilities for WL Commands."""

import fnmatch
import shutil
from pathlib import Path


class FileOperationResult:
    """Result of a file operation."""

    def __init__(
        self, success: bool, message: str = "", files_affected: list[str] | None = None
    ):
        self.success = success
        self.message = message
        self.files_affected = files_affected or []


class FileOperationsCache:
    """Cache for file operations to avoid redundant operations."""

    def __init__(self):
        self._existence_cache: dict[str, bool] = {}
        self._directory_contents_cache: dict[str, list[str]] = {}

    def clear(self) -> None:
        """Clear the cache."""
        self._existence_cache.clear()
        self._directory_contents_cache.clear()


class FileOperations:
    """Unified file operations utility class."""

    def __init__(self):
        self.cache = FileOperationsCache()

    def exists(self, path: str | Path) -> bool:
        """
        Check if a path exists.

        Args:
            path: Path to check

        Returns:
            True if path exists, False otherwise
        """
        path_str = str(path)
        if path_str in self.cache._existence_cache:
            return self.cache._existence_cache[path_str]

        result = Path(path).exists()
        self.cache._existence_cache[path_str] = result
        return result

    def get_files_in_directory(
        self, directory: str | Path, pattern: str = "*", recursive: bool = True
    ) -> list[Path]:
        """
        Get all files in a directory matching a pattern.

        Args:
            directory: Directory to search
            pattern: File pattern to match (e.g., "*.py")
            recursive: Whether to search recursively

        Returns:
            List of matching files
        """
        directory_str = str(directory)
        cache_key = f"{directory_str}:{pattern}:{recursive}"

        if cache_key in self.cache._directory_contents_cache:
            # Convert cached strings back to Path objects
            return [Path(p) for p in self.cache._directory_contents_cache[cache_key]]

        dir_path = Path(directory)
        if not self.exists(dir_path):
            self.cache._directory_contents_cache[cache_key] = []
            return []

        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))

        # Cache the result as strings
        file_strings = [str(f) for f in files]
        self.cache._directory_contents_cache[cache_key] = file_strings

        return files

    def copy_file(self, src: str | Path, dst: str | Path) -> FileOperationResult:
        """
        Copy a file from src to dst.

        Args:
            src: Source file path
            dst: Destination file path

        Returns:
            FileOperationResult indicating success or failure
        """
        try:
            src_path = Path(src)
            dst_path = Path(dst)

            if not self.exists(src_path):
                return FileOperationResult(
                    False, f"Source file does not exist: {src_path}"
                )

            # Create parent directories if they don't exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(src_path, dst_path)
            return FileOperationResult(
                True, f"Successfully copied {src_path} to {dst_path}", [str(dst_path)]
            )
        except Exception as e:
            return FileOperationResult(
                False, f"Failed to copy file from {src} to {dst}: {str(e)}"
            )

    def copy_directory(
        self,
        src: str | Path,
        dst: str | Path,
        exclude_patterns: list[str] | None = None,
    ) -> FileOperationResult:
        """
        Copy a directory from src to dst.

        Args:
            src: Source directory path
            dst: Destination directory path
            exclude_patterns: List of patterns to exclude (e.g., ["*.tmp", "__pycache__"])

        Returns:
            FileOperationResult indicating success or failure
        """
        try:
            src_path = Path(src)
            dst_path = Path(dst)

            if not self.exists(src_path):
                return FileOperationResult(
                    False, f"Source directory does not exist: {src_path}"
                )

            if not src_path.is_dir():
                return FileOperationResult(
                    False, f"Source path is not a directory: {src_path}"
                )

            # Create destination directory
            dst_path.mkdir(parents=True, exist_ok=True)

            copied_files = []

            for item in src_path.rglob("*"):
                # Skip excluded patterns
                if exclude_patterns:
                    should_exclude = False
                    for pattern in exclude_patterns:
                        if fnmatch.fnmatch(item.name, pattern) or fnmatch.fnmatch(
                            str(item.relative_to(src_path)), pattern
                        ):
                            should_exclude = True
                            break
                    if should_exclude:
                        continue

                relative_path = item.relative_to(src_path)
                dst_item = dst_path / relative_path

                if item.is_file():
                    dst_item.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst_item)
                    copied_files.append(str(dst_item))
                elif item.is_dir():
                    dst_item.mkdir(parents=True, exist_ok=True)

            return FileOperationResult(
                True,
                f"Successfully copied directory {src_path} to {dst_path}",
                copied_files,
            )
        except Exception as e:
            return FileOperationResult(
                False, f"Failed to copy directory from {src} to {dst}: {str(e)}"
            )

    def remove_directory(self, directory: str | Path) -> FileOperationResult:
        """
        Remove a directory and all its contents.

        Args:
            directory: Directory to remove

        Returns:
            FileOperationResult indicating success or failure
        """
        try:
            dir_path = Path(directory)

            if not self.exists(dir_path):
                return FileOperationResult(
                    True, f"Directory does not exist: {dir_path}"
                )

            if not dir_path.is_dir():
                return FileOperationResult(
                    False, f"Path is not a directory: {dir_path}"
                )

            shutil.rmtree(dir_path)
            return FileOperationResult(
                True, f"Successfully removed directory {dir_path}"
            )
        except Exception as e:
            return FileOperationResult(
                False, f"Failed to remove directory {directory}: {str(e)}"
            )

    def clear_cache(self) -> None:
        """Clear the file operations cache."""
        self.cache.clear()


# Global instance
_file_operations = FileOperations()


def get_file_operations() -> FileOperations:
    """
    Get the global file operations instance.

    Returns:
        The global file operations instance
    """
    return _file_operations
