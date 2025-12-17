"""Package building for publish command."""

import shutil
import subprocess
from pathlib import Path

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info


class PackageBuilder:
    """Handle package building operations for the publish command."""

    def build_distribution_packages(self) -> None:
        """Build distribution packages using wl build dist command."""
        log_info("Building distribution packages with 'wl build dist'...")
        log_info("使用 'wl build dist' 构建分发包...", lang="zh")

        # Clean previous builds
        dist_dir = Path("dist")
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
            dist_dir.mkdir(exist_ok=True)

        log_info("Running: wl build dist")
        # Execute wl build dist command and let it output directly to stdout/stderr
        # This allows us to see the maturin build process in real-time
        try:
            result = subprocess.run(
                ["wl", "build", "dist"],
                check=True,
                capture_output=False,
                text=True,
            )

            log_info("✓ Distribution packages built successfully with 'wl build dist'")
            log_info("✓ 分发包通过 'wl build dist' 成功构建", lang="zh")

            # Ensure dist directory exists after build
            dist_dir.mkdir(exist_ok=True)

            # List files in dist directory for verification
            if dist_dir.exists():
                dist_files = list(dist_dir.iterdir())
                log_info(f"Files in dist directory: {[f.name for f in dist_files]}")

        except subprocess.CalledProcessError as e:
            error_message = (
                f"Build failed with return code: {e.returncode}"
                if e is not None
                else "Build failed with CalledProcessError"
            )
            log_error(error_message)
            raise CommandError(error_message)
        except Exception as e:
            error_message = str(e) if e is not None else "Unknown build error occurred"
            log_error(f"Build failed: {error_message}")
            raise CommandError(f"Build failed: {error_message}")

    def get_dist_files(self):
        """Get distribution files from dist directory."""
        dist_dir = Path("dist")
        if not dist_dir.exists():
            dist_dir.mkdir(exist_ok=True)
            return []

        # Refresh directory contents
        dist_dir = Path("dist")
        files = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
        return files
