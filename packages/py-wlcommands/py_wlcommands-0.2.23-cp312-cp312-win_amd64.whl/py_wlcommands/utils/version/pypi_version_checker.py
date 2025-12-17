"""
PyPI version checking utilities for publish command.
"""

import json
from urllib import request
from urllib.error import URLError

import aiohttp

from ...exceptions import CommandError
from ..logging import log_info


class PyPIVersionChecker:
    """Check versions against PyPI servers."""

    def _get_pypi_version(self) -> str | None:
        """Get the latest version from PyPI."""
        package_name = "py_wlcommands"
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            with request.urlopen(url) as response:
                data = json.loads(response.read())
            return data["info"]["version"]
        except (OSError, json.JSONDecodeError, KeyError):
            # If we can't get the PyPI version, return None
            return None

    async def _get_pypi_version_async(self) -> str | None:
        """Async get the latest version from PyPI."""
        package_name = "py_wlcommands"
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
            return data["info"]["version"]
        except (OSError, json.JSONDecodeError, KeyError, aiohttp.ClientError):
            # If we can't get the PyPI version, return None
            return None

    def check_version_with_pypi(
        self, repository: str, current_version: str, comparator
    ) -> None:
        """Check the current version against PyPI to ensure proper versioning."""
        package_name = (
            "py_wlcommands"  # This should ideally be read from project config
        )

        try:
            # Determine the repository URL
            if repository == "pypi":
                url = f"https://pypi.org/pypi/{package_name}/json"
            else:
                # For other repositories, we might need to get the URL from twine config
                # For now, we'll assume it's TestPyPI
                url = f"https://test.pypi.org/pypi/{package_name}/json"

            log_info(f"Checking version on {repository} server...")
            log_info(f"正在检查 {repository} 服务器上的版本...", lang="zh")

            # Make request to PyPI API
            with request.urlopen(url) as response:
                data = json.loads(response.read())

            # Get the latest version from PyPI
            pypi_version = data["info"]["version"]
            log_info(f"Latest version on {repository}: {pypi_version}")
            log_info(f"{repository} 上的最新版本: {pypi_version}", lang="zh")

            # Compare versions
            if not comparator.is_version_increment_valid(pypi_version, current_version):
                raise CommandError(
                    f"Version check failed: Local version {current_version} "
                    f"is not a valid increment from PyPI version {pypi_version}. "
                    f"Version must be incremented and not skip numbers."
                )

            log_info("✓ Version check passed")
            log_info("✓ 版本检查通过", lang="zh")

        except URLError as e:
            log_info(f"Warning: Could not check version on PyPI: {e}")
            log_info(f"警告: 无法检查 PyPI 上的版本: {e}", lang="zh")
        except (json.JSONDecodeError, KeyError) as e:
            log_info(f"Warning: Version check failed: {e}")
            log_info(f"警告: 版本检查失败: {e}", lang="zh")

    async def check_version_with_pypi_async(
        self, repository: str, current_version: str, comparator
    ) -> None:
        """Async check the current version against PyPI to ensure proper versioning."""
        package_name = (
            "py_wlcommands"  # This should ideally be read from project config
        )

        try:
            # Determine the repository URL
            if repository == "pypi":
                url = f"https://pypi.org/pypi/{package_name}/json"
            else:
                # For other repositories, we might need to get the URL from twine config
                # For now, we'll assume it's TestPyPI
                url = f"https://test.pypi.org/pypi/{package_name}/json"

            log_info(f"Checking version on {repository} server...")
            log_info(f"正在检查 {repository} 服务器上的版本...", lang="zh")

            # Make async request to PyPI API
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()

            # Get the latest version from PyPI
            pypi_version = data["info"]["version"]
            log_info(f"Latest version on {repository}: {pypi_version}")
            log_info(f"{repository} 上的最新版本: {pypi_version}", lang="zh")

            # Compare versions
            if not comparator.is_version_increment_valid(pypi_version, current_version):
                raise CommandError(
                    f"Version check failed: Local version {current_version} "
                    f"is not a valid increment from PyPI version {pypi_version}. "
                    f"Version must be incremented and not skip numbers."
                )

            log_info("✓ Version check passed")
            log_info("✓ 版本检查通过", lang="zh")

        except aiohttp.ClientError as e:
            log_info(f"Warning: Could not check version on PyPI: {e}")
            log_info(f"警告: 无法检查 PyPI 上的版本: {e}", lang="zh")
        except (json.JSONDecodeError, KeyError) as e:
            log_info(f"Warning: Version check failed: {e}")
            log_info(f"警告: 版本检查失败: {e}", lang="zh")
