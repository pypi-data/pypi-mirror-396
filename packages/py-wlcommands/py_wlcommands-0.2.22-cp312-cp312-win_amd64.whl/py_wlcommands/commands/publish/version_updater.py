"""
Version updating utilities for publish command.
"""

import re
from pathlib import Path

from ...exceptions import CommandError
from ...utils.logging import log_info


class VersionUpdater:
    """Update versions in project files."""

    def _update_python_version(self, new_version: str) -> None:
        """Update the Python __init__.py file with a specific version."""
        python_version_file = Path("src/py_wlcommands/__init__.py")
        if python_version_file.exists():
            try:
                content = python_version_file.read_text(encoding="utf-8")
                # Find version pattern and replace with new version
                version_pattern = r'(__version__\s*=\s*["\'])((\d+\.\d+\.\d+))(["\'])'
                match = re.search(version_pattern, content)
                if match:
                    prefix = match.group(1)
                    suffix = match.group(4)
                    new_content = f"{prefix}{new_version}{suffix}"
                    updated_content = re.sub(version_pattern, new_content, content)
                    python_version_file.write_text(updated_content, encoding="utf-8")
                    log_info(f"Updated Python version to {new_version}")
            except Exception as e:
                raise CommandError(f"Failed to update Python version: {e}")

    def _update_rust_version(self, new_version: str) -> None:
        """Update the Rust Cargo.toml file with a specific version."""
        rust_version_file = Path("rust/Cargo.toml")
        if rust_version_file.exists():
            try:
                content = rust_version_file.read_text(encoding="utf-8")
                # Find version pattern in [package] section and replace with new version
                package_section_pattern = (
                    r'(\[package\][^\[]*version\s*=\s*["\'])((\d+\.\d+\.\d+))(["\'])'
                )
                match = re.search(package_section_pattern, content, re.DOTALL)
                if match:
                    prefix = match.group(1)
                    suffix = match.group(4)
                    new_content = f"{prefix}{new_version}{suffix}"
                    updated_content = re.sub(
                        package_section_pattern, new_content, content, flags=re.DOTALL
                    )
                    rust_version_file.write_text(updated_content, encoding="utf-8")
                    log_info(f"Updated Rust version to {new_version}")
            except Exception as e:
                raise CommandError(f"Failed to update Rust version: {e}")

    def increment_version(
        self, detector, comparator, pypi_checker=None, dry_run: bool = False
    ) -> None:
        """Increment the version to be greater than both local and PyPI versions.

        Args:
            detector: Version detector to get current version.
            comparator: Version comparator to compare and increment versions.
            pypi_checker: PyPI version checker (optional).
            dry_run: Whether to perform a dry run without modifying files.
        """
        log_info("Checking versions and incrementing as needed...")
        log_info("正在检查版本并根据需要递增...", lang="zh")

        # Get current PyPI version
        pypi_version = None
        if pypi_checker:
            try:
                pypi_version = pypi_checker._get_pypi_version()
            except Exception:
                # If getting PyPI version fails, use None
                pass
        else:
            # Backward compatibility: try to get PyPI version from detector
            try:
                if hasattr(detector, "_get_pypi_version"):
                    pypi_version = detector._get_pypi_version()
            except Exception:
                pass
        if pypi_version:
            log_info(f"Latest version on PyPI: {pypi_version}")
            log_info(f"PyPI 上的最新版本: {pypi_version}", lang="zh")

        # Get current local version
        current_version = detector.get_current_version(comparator)
        log_info(f"Current local version: {current_version}")
        log_info(f"当前本地版本: {current_version}", lang="zh")

        # Determine which version to use as base for incrementing
        if pypi_version:
            # Compare versions and use the greater one as base
            greater_version = comparator.get_greater_version(
                pypi_version, current_version
            )
            log_info(f"Greater version between local and PyPI: {greater_version}")
            log_info(f"本地和 PyPI 之间较大的版本: {greater_version}", lang="zh")

            # Always increment the version regardless of whether they are equal or not
            new_version = comparator.increment_version_from_base(greater_version)
        else:
            # If we can't get PyPI version, increment local version
            new_version = comparator.increment_version_from_base(current_version)

        log_info(f"New version to be set: {new_version}")
        log_info(f"将要设置的新版本: {new_version}", lang="zh")

        if dry_run:
            log_info("Dry run mode: Would update version files")
            log_info("Dry run mode: 将更新版本文件", lang="zh")
        else:
            # Update both Python and Rust versions
            self._update_python_version(new_version)
            self._update_rust_version(new_version)
