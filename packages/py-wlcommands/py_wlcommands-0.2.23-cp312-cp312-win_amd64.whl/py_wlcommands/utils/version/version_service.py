"""Version management service for publish command."""

# Handle aiohttp import gracefully
from types import ModuleType
from typing import Optional, Type

# Define variables with proper types first
aiohttp: ModuleType | None = None
ClientError: type[Exception] = Exception

try:
    import aiohttp as _aiohttp

    aiohttp = _aiohttp
    ClientError = _aiohttp.ClientError
except ImportError:
    pass

from ...exceptions import CommandError
from ..logging import log_info

# Import modular components
from .pypi_version_checker import PyPIVersionChecker
from .version_comparator import VersionComparator
from .version_detectors import VersionDetector
from .version_updater import VersionUpdater


class VersionService:
    """Manage version operations for the publish command."""

    def __init__(self):
        """Initialize version service with component handlers."""
        self.comparator = VersionComparator()
        self.detector = VersionDetector()
        self.pypi_checker = PyPIVersionChecker()
        self.updater = VersionUpdater()

        # 动态替换_get_pypi_version方法到detector对象，保持向后兼容性
        # 这是为了支持直接调用detector._get_pypi_version()的代码
        # 创建一个方法，每次调用时动态访问service实例
        def _get_pypi_version():
            # 使用闭包保存service引用
            return self.pypi_checker._get_pypi_version()

        # 将方法绑定到detector对象（替换原有方法）
        self.detector._get_pypi_version = _get_pypi_version

    def get_current_version(self) -> str:
        """Get the current version from Cargo.toml or __init__.py."""
        return self.detector.get_current_version(self.comparator)

    def check_version_with_pypi(self, repository: str, current_version: str) -> None:
        """Check the current version against PyPI to ensure proper versioning."""
        self.pypi_checker.check_version_with_pypi(
            repository, current_version, self.comparator
        )

    async def check_version_with_pypi_async(
        self, repository: str, current_version: str
    ) -> None:
        """Async check the current version against PyPI to ensure proper versioning."""
        package_name = "py_wlcommands"

        try:
            # Determine the repository URL
            if repository == "pypi":
                url = f"https://pypi.org/pypi/{package_name}/json"
            else:
                url = f"https://test.pypi.org/pypi/{package_name}/json"

            log_info(f"Checking version on {repository} server...")
            log_info(f"正在检查 {repository} 服务器上的版本...", lang="zh")

            # Make async request to PyPI API
            if aiohttp is None:
                log_info("Warning: aiohttp is not available, skipping async PyPI check")
                log_info("警告: aiohttp 不可用，跳过异步 PyPI 检查", lang="zh")
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()

            # Get the latest version from PyPI
            pypi_version = data["info"]["version"]
            log_info(f"Latest version on {repository}: {pypi_version}")
            log_info(f"{repository} 上的最新版本: {pypi_version}", lang="zh")

            # Compare versions
            if not self.comparator.is_version_increment_valid(
                pypi_version, current_version
            ):
                raise CommandError(
                    f"Version check failed: Local version {current_version} "
                    f"is not a valid increment from PyPI version {pypi_version}. "
                    f"Version must be incremented and not skip numbers."
                )

            log_info("✓ Version check passed")
            log_info("✓ 版本检查通过", lang="zh")

        except Exception as e:
            log_info(f"Warning: Could not check version on PyPI: {e}")
            log_info(f"警告: 无法检查 PyPI 上的版本: {e}", lang="zh")

    def increment_version(self, dry_run: bool = False):
        """
        增量更新版本号

        Args:
            dry_run: 是否为模拟运行，不实际修改文件
        """
        self.updater.increment_version(
            self.detector, self.comparator, self.pypi_checker, dry_run
        )

    async def increment_version_async(self, dry_run: bool = False) -> None:
        """Async increment the version to be greater than both local and PyPI versions."""
        log_info("Checking versions and incrementing as needed...")
        log_info("正在检查版本并根据需要递增...", lang="zh")

        # Get current local version
        current_version = self.detector.get_current_version(self.comparator)
        log_info(f"Current local version: {current_version}")
        log_info(f"当前本地版本: {current_version}", lang="zh")

        # Get current PyPI version async
        pypi_version = None
        try:
            package_name = "py_wlcommands"
            url = f"https://pypi.org/pypi/{package_name}/json"
            if aiohttp is None:
                log_info("Warning: aiohttp is not available, skipping async PyPI check")
                log_info("警告: aiohttp 不可用，跳过异步 PyPI 检查", lang="zh")
                return

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    pypi_version = data["info"]["version"]
                    log_info(f"Latest version on PyPI: {pypi_version}")
                    log_info(f"PyPI 上的最新版本: {pypi_version}", lang="zh")
        except Exception as e:
            log_info(f"Warning: Could not get PyPI version: {e}")
            log_info(f"警告: 无法获取 PyPI 版本: {e}", lang="zh")

        # Determine which version to use as base for incrementing
        if pypi_version:
            # Compare versions and use the greater one as base
            greater_version = self.comparator.get_greater_version(
                pypi_version, current_version
            )
            log_info(f"Greater version between local and PyPI: {greater_version}")
            log_info(f"本地和 PyPI 之间较大的版本: {greater_version}", lang="zh")

            # Always increment the version regardless of whether they are equal or not
            new_version = self.comparator.increment_version_from_base(greater_version)
        else:
            # If we can't get PyPI version, increment local version
            new_version = self.comparator.increment_version_from_base(current_version)

        log_info(f"New version to be set: {new_version}")
        log_info(f"将要设置的新版本: {new_version}", lang="zh")

        if dry_run:
            log_info("Dry run mode: Would update version files")
            log_info("Dry run mode: 将更新版本文件", lang="zh")
        else:
            # Update both Python and Rust versions
            self.updater._update_python_version(new_version)
            self.updater._update_rust_version(new_version)
