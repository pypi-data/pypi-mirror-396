"""PyPI uploading for publish command."""

import os
import subprocess

from ...exceptions import CommandError
from ...utils.logging import log_info
from ...utils.subprocess_utils import SubprocessExecutor


class PyPIUploader:
    """Handle PyPI uploading operations for the publish command."""

    def _check_twine_available(self):
        """Check if twine is available in the system."""
        executor = SubprocessExecutor()

        # Try different ways to call twine
        twine_commands = [
            ["twine", "--version"],
            ["python", "-m", "twine", "--version"],
            ["uv", "tool", "run", "twine", "--version"],
        ]

        for cmd in twine_commands:
            try:
                result = executor.run(cmd, quiet=True)
                if result.success:
                    return True
            except Exception:
                continue

        return False

    def upload_to_pypi(self, repository: str, dist_files, username=None, password=None):
        """Upload distribution files to PyPI."""
        # Check if twine is available
        twine_available = self._check_twine_available()
        if not twine_available:
            raise CommandError(
                "twine is not installed. Please install it with 'pip install twine' or 'uv tool install twine'"
            )

        # Build twine command
        cmd = ["twine", "upload"]
        if repository != "pypi":
            cmd.extend(["--repository", repository])
        if username:
            cmd.extend(["--username", username])
        if password:
            cmd.extend(["--password", password])

        # Disable proxy to avoid connection issues
        cmd.extend(["--disable-progress-bar"])

        # Add all dist files
        for f in dist_files:
            cmd.append(str(f))

        # Prepare environment without proxy settings
        env = os.environ.copy()
        env.pop("HTTP_PROXY", None)
        env.pop("HTTPS_PROXY", None)
        env.pop("http_proxy", None)
        env.pop("https_proxy", None)

        log_info(f"Uploading to {repository} with command: {' '.join(cmd)}")
        executor = SubprocessExecutor()
        result = executor.run(cmd, quiet=False, env=env)
        if not result.success:
            error_msg = result.stderr or result.stdout
            if "ProxyError" in error_msg:
                log_info("Proxy error detected. Trying again with proxy disabled...")
                # Try again with explicit proxy disabling
                cmd.extend(
                    [
                        "--trusted-host",
                        "upload.pypi.org",
                        "--trusted-host",
                        "pypi.org",
                        "--trusted-host",
                        "files.pythonhosted.org",
                    ]
                )
                result = executor.run(cmd, quiet=False, env=env)
                if not result.success:
                    raise CommandError(
                        f"Upload failed: {result.stderr or result.stdout}"
                    )
            else:
                raise CommandError(f"Upload failed: {error_msg}")
