"""Publish command implementation for WL Commands."""

import argparse
import asyncio
from pathlib import Path
from typing import Any

from ...commands import Command, register_command
from ...exceptions import CommandError
from ...utils.logging import log_error, log_info
from ...utils.version import VersionService
from .package_builder import PackageBuilder
from .pypi_uploader import PyPIUploader


@register_command("publish")
class PublishCommand(Command):
    """Publish command for WL Commands."""

    def __init__(self):
        """Initialize the publish command."""
        self.impl = PublishCommandImpl()

    @property
    def name(self) -> str:
        """Return the command name."""
        return self.impl.name

    @property
    def help(self) -> str:
        """Return the command help text."""
        return self.impl.help

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add arguments to the parser."""
        self.impl.add_arguments(parser)

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Execute the publish command."""
        try:
            self.impl.execute(*args, **kwargs)
        except Exception as e:
            # 确保我们处理的是一个有效的异常对象
            error_message = str(e) if e is not None else "Unknown error occurred"
            log_error(f"Publish failed: {error_message}")
            log_error(f"发布失败: {error_message}", lang="zh")
            raise CommandError(f"Publish failed: {error_message}")


class PublishCommandImpl:
    """Implementation of the publish command."""

    def __init__(self):
        """Initialize the publish command."""
        self.version_service = VersionService()
        self.package_builder = PackageBuilder()
        self.uploader = PyPIUploader()

    @property
    def name(self) -> str:
        """Return the command name."""
        return "publish"

    @property
    def help(self) -> str:
        """Return the command help text."""
        return "Publish the project to PyPI"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add arguments to the parser."""
        parser.add_argument(
            "--repository",
            "-r",
            default="pypi",
            help="Repository to upload to (default: pypi)",
        )
        parser.add_argument(
            "--skip-build",
            action="store_true",
            help="Skip building the package, use existing dist files",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without actually uploading",
        )
        parser.add_argument(
            "--username",
            help="Username for uploading to PyPI",
        )
        parser.add_argument(
            "--password",
            help="Password or API token for uploading to PyPI",
        )
        parser.add_argument(
            "--no-auto-increment",
            action="store_true",
            help="Do not automatically increment the patch version before publishing",
        )
        parser.add_argument(
            "--skip-version-check",
            action="store_true",
            help="Skip version check against PyPI server",
        )

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Execute the publish command."""
        # Run async implementation using asyncio.run
        asyncio.run(self._execute_async(*args, **kwargs))

    async def _execute_async(self, *args: Any, **kwargs: Any) -> None:
        """Async implementation of the publish command."""
        repository = kwargs.get("repository", "pypi")
        skip_build = kwargs.get("skip_build", False)
        dry_run = kwargs.get("dry_run", False)
        username = kwargs.get("username")
        password = kwargs.get("password")
        no_auto_increment = kwargs.get("no_auto_increment", False)
        skip_version_check = kwargs.get("skip_version_check", False)

        try:
            # Get current version
            current_version = self.version_service.get_current_version()
            log_info(f"Current local version: {current_version}")

            # Check version against PyPI unless explicitly skipped
            if not skip_version_check:
                await self._check_pypi_version_async(repository, current_version)

            # Auto increment version unless explicitly disabled
            if not no_auto_increment and not dry_run:
                log_info("Incrementing version...")
                await self.version_service.increment_version_async(dry_run=False)
                # After incrementing version, we need to rebuild
                # If user specified skip_build, we ignore that since version changed
                skip_build = False
            elif not no_auto_increment and dry_run:
                log_info("Dry run mode: Would increment version")
                log_info("Dry run mode: 将递增版本号", lang="zh")
                # For dry run, we can use the sync method since no actual changes are made
                self.version_service.increment_version(dry_run=True)

            # Build the project if not skipped
            if not skip_build and not dry_run:
                self.package_builder.build_distribution_packages()
            elif not skip_build and dry_run:
                log_info(
                    "Dry run mode: Would build distribution packages with 'wl build dist'"
                )
                log_info(
                    "Dry run mode: 将使用 'wl build dist' 构建分发包...", lang="zh"
                )

            # Always get distribution files directly from dist directory
            dist_path = Path("dist")
            if dist_path.exists():
                dist_files = list(dist_path.glob("*.whl")) + list(
                    dist_path.glob("*.tar.gz")
                )
            else:
                dist_files = []

            # Process distribution files and upload
            wheel_files = self._process_dist_files(dist_files, skip_build, dry_run)

            # Upload to PyPI
            if not dry_run:
                await self._handle_upload(
                    repository, wheel_files, dry_run, username or "", password or ""
                )
                log_info("✓ Package published successfully!")
                log_info("✓ 包发布成功！", lang="zh")
            else:
                log_info("Dry run mode: Would upload to PyPI")
                log_info("Dry run mode: 将上传到 PyPI", lang="zh")
                log_info("✓ Dry run completed successfully!")
                log_info("✓ 干运行完成！", lang="zh")

        except Exception as e:
            # 确保我们处理的是一个有效的异常对象
            error_message = str(e) if e is not None else "Unknown error occurred"
            log_error(f"Publish failed: {error_message}")
            log_error(f"发布失败: {error_message}", lang="zh")
            raise CommandError(f"Publish failed: {error_message}")

    async def _check_pypi_version_async(
        self, repository: str, current_version: str
    ) -> None:
        """Async check version against PyPI server."""
        try:
            await self.version_service.check_version_with_pypi_async(
                repository, current_version
            )
        except Exception as e:
            # If version check fails, we should still allow publishing if explicitly requested
            log_info(f"Warning: Version check failed: {e}")

    def _process_dist_files(
        self, dist_files: list, skip_build: bool, dry_run: bool
    ) -> list:
        """Process distribution files and return wheel files."""
        log_info(f"Processing dist files. Count: {len(dist_files)}")
        log_info(f"Files: {[str(f) for f in dist_files]}")

        files = self._collect_dist_files(dist_files)
        log_info(f"After checking dist/, files count: {len(files)}")

        if not skip_build and not dry_run and not files:
            raise CommandError("No distribution files found in dist/ directory")

        wheel_files = self._extract_wheel_files(files)
        log_info(f"Wheel files count: {len(wheel_files)}")

        if not wheel_files and not skip_build and not dry_run:
            raise CommandError(
                "No wheel files found in dist/ directory. Run 'wl build dist' first."
            )

        if wheel_files:
            log_info(f"Found {len(wheel_files)} wheel files to upload")
            for f in wheel_files:
                log_info(f"  - {getattr(f, 'name', str(f))}")

        return wheel_files

    def _collect_dist_files(self, dist_files: list) -> list:
        """Collect distribution files from provided list or dist directory."""
        if dist_files:
            return dist_files

        dist_path = Path("dist")
        if dist_path.exists():
            direct_files = list(dist_path.glob("*.whl")) + list(
                dist_path.glob("*.tar.gz")
            )
            if direct_files:
                return direct_files
        return []

    def _extract_wheel_files(self, files: list) -> list:
        """Extract wheel files from a list of files."""
        wheels: list = []
        for f in files:
            if isinstance(f, Path) and f.suffix == ".whl":
                wheels.append(f)
            elif hasattr(f, "name") and str(getattr(f, "name", f)).endswith(".whl"):
                wheels.append(f)
            elif getattr(f, "suffix", None) == ".whl":
                wheels.append(f)
        return wheels

    async def _handle_upload(
        self,
        repository: str,
        wheel_files: list,
        dry_run: bool,
        username: str,
        password: str,
    ) -> None:
        """Handle the upload process."""
        if dry_run:
            log_info("Dry run: No files will be uploaded.")
            return

        if wheel_files:
            # upload_to_pypi is currently sync, but we can call it directly in async context
            self.uploader.upload_to_pypi(repository, wheel_files, username, password)
