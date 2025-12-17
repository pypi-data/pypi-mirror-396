"""Packaging module for publish command."""

import shutil
from pathlib import Path

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info
from ...utils.subprocess_utils import SubprocessExecutor


class Packager:
    """Handle package operations for the publish command."""

    def __init__(self):
        """Initialize the packager."""
        self.executor = SubprocessExecutor()
        # 移除format_manager，使用简单的文件过滤代替

    def clean_dist_directory(self) -> None:
        """Clean the dist directory."""
        dist_dir = Path("dist")
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        dist_dir.mkdir(exist_ok=True)

    def build_distribution_packages(self) -> None:
        """Build distribution packages using wl build dist command."""
        log_info("Building distribution packages with 'wl build dist'...")
        log_info("使用 'wl build dist' 构建分发包...", lang="zh")

        # Clean previous builds
        self.clean_dist_directory()

        log_info("Running: wl build dist")
        # Execute wl build dist command and let it output directly to stdout/stderr
        # This allows us to see the maturin build process in real-time
        try:
            result = self.executor.run(["wl", "build", "dist"], quiet=False)

            log_info("✓ Distribution packages built successfully with 'wl build dist'")
            log_info("✓ 分发包通过 'wl build dist' 成功构建", lang="zh")

            # Ensure dist directory exists after build
            dist_dir = Path("dist")
            dist_dir.mkdir(exist_ok=True)

            # List files in dist directory for verification
            if dist_dir.exists():
                dist_files = list(dist_dir.iterdir())
                log_info(f"Files in dist directory: {[f.name for f in dist_files]}")

        except Exception as e:
            error_message = str(e) if e is not None else "Unknown build error occurred"
            log_error(f"Build failed: {error_message}")
            raise CommandError(f"Build failed: {error_message}")

    def get_dist_files(self) -> list[Path]:
        """Get distribution files from dist directory."""
        dist_dir = Path("dist")
        if not dist_dir.exists():
            dist_dir.mkdir(exist_ok=True)
            return []

        # Refresh directory contents
        dist_dir = Path("dist")
        # 简单实现获取所有文件
        return list(dist_dir.iterdir()) if dist_dir.exists() else []

    def collect_dist_files(self, dist_files: list[Path] | None = None) -> list[Path]:
        """Collect distribution files from provided list or dist directory."""
        if dist_files:
            return dist_files

        dist_path = Path("dist")
        if dist_path.exists():
            # 简单实现获取所有文件
            direct_files = list(dist_path.iterdir()) if dist_path.exists() else []
            if direct_files:
                return direct_files
        return []

    def extract_wheel_files(self, files: list[Path]) -> list[Path]:
        """Extract wheel files from a list of files."""
        # 简单实现过滤wheel文件
        return [f for f in files if f.suffix == ".whl"]
