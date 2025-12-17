"""UV workspace detection utilities for WL Commands."""

import subprocess
from pathlib import Path

from .logging import log_info
from .subprocess_utils import SubprocessExecutor


class UVWorkspaceDetector:
    """A utility class for detecting UV workspaces."""

    def __init__(self):
        self._subprocess_executor = SubprocessExecutor()
        self._workspace_cache = {}

    def is_workspace(self, project_root: Path | None = None) -> bool:
        """
        Detect if we are in a uv workspace.

        Args:
            project_root: The project root directory. If None, uses current directory.

        Returns:
            True if in a workspace, False otherwise.
        """
        try:
            if project_root is None:
                project_root = Path.cwd()

            project_root = project_root.resolve()
            root_str = str(project_root)

            # Check cache first
            if root_str in self._workspace_cache:
                return self._workspace_cache[root_str]

            # Method 1: Check for uv.lock file which indicates a workspace
            uv_lock_path = project_root / "uv.lock"
            if uv_lock_path.exists() and uv_lock_path.is_file():
                log_info("Debug: uv.lock file found, workspace detected")
                self._workspace_cache[root_str] = True
                return True

            # Method 2: Use uv init command to check if we're already in a workspace
            try:
                result = self._subprocess_executor.run(
                    ["uv", "init", "--dry-run"], cwd=project_root, quiet=True
                )

                if (
                    result.success
                    and "is already a member of workspace" in result.stderr
                ):
                    log_info("Debug: 'is already a member of workspace' detected")
                    self._workspace_cache[root_str] = True
                    return True
            except (subprocess.SubprocessError, OSError, ValueError):
                # Fall back to other methods if uv init fails
                pass

            # Method 3: Use uv tree command to check for multiple root packages
            is_workspace_result = self._detect_workspace_via_tree(project_root)
            self._workspace_cache[root_str] = is_workspace_result
            return is_workspace_result

        except (OSError, ValueError) as e:
            log_info(f"Debug: Workspace detection error: {e}")
            # Cache the result even for errors to avoid repeated failures
            # Use a default key if root_str is not defined
            cache_key = root_str if "root_str" in locals() else "error_default"
            self._workspace_cache[cache_key] = False
            return False

    def _detect_workspace_via_tree(self, project_root: Path) -> bool:
        """
        Detect workspace using uv tree command.

        Args:
            project_root: The project root directory.

        Returns:
            True if workspace detected, False otherwise.
        """
        try:
            result = self._subprocess_executor.run(
                ["uv", "tree"], cwd=project_root, quiet=True
            )

            if not result.success:
                log_info(f"Debug: uv tree command failed with code {result.returncode}")
                return False

            # Check for a workspace by counting root packages
            # In a workspace, there would be multiple top-level packages
            lines = result.stdout.split("\n") if result.stdout else []
            root_packages = self._parse_root_packages(lines)

            log_info(f"Debug: uv tree root packages: {root_packages}")
            log_info(f"Debug: root packages count: {len(root_packages)}")

            # There should be more than one root package in a workspace
            if len(root_packages) > 1:
                log_info("Debug: Multiple root packages found, workspace detected")
                return True

        except (subprocess.SubprocessError, OSError, ValueError) as e:
            log_info(f"Debug: Workspace detection via tree error: {e}")
            pass  # Ignore errors in workspace detection

        log_info("Debug: No workspace detected via tree")
        return False

    def _parse_root_packages(self, lines: list[str]) -> list[str]:
        """
        Parse root packages from uv tree output.

        Args:
            lines: Lines from uv tree output.

        Returns:
            List of root package names.
        """
        root_packages = []
        for line in lines:
            # Root package lines:
            # 1. Are not indented (don't start with space)
            # 2. Are not "Resolved" lines
            # 3. Are not "(*)" lines
            if (
                not line.startswith(" ")
                and line.strip()
                and not line.startswith("Resolved")
                and not line.startswith("(*)")
            ):
                # Check if this is a root package - either without version or with version
                # Root packages with versions look like "package-name v1.2.3"
                if " v" in line and not line.startswith("v"):
                    # Check if it's a root package with version by verifying the format
                    parts = line.split(" v", 1)  # Split only on first occurrence
                    if len(parts) == 2:
                        package_name = parts[0]
                        version = parts[1]
                        # Verify that package name doesn't start with special chars and version is valid
                        if (
                            package_name
                            and not package_name.startswith(("├", "└", "│"))
                            and self._is_valid_version(version)
                        ):
                            root_packages.append(package_name)
                elif line and not line.startswith(
                    ("├", "└", "│")
                ):  # Plain root package without version
                    root_packages.append(line.strip())

        return root_packages

    def _is_valid_version(self, version: str) -> bool:
        """
        Check if a version string is valid.

        Args:
            version: Version string to check.

        Returns:
            True if valid, False otherwise.
        """
        # A valid version should only contain alphanumeric characters, dots, and hyphens
        # Also handle empty strings
        if not version:
            return False
        return all(c.isalnum() or c in ".-+" for c in version)

    def clear_cache(self) -> None:
        """Clear the workspace detection cache."""
        self._workspace_cache.clear()


# Global instance
_uv_workspace_detector = UVWorkspaceDetector()


def is_uv_workspace(project_root: Path | None = None) -> bool:
    """
    Detect if we are in a uv workspace.

    Args:
        project_root: The project root directory. If None, uses current directory.

    Returns:
        True if in a workspace, False otherwise.
    """
    return _uv_workspace_detector.is_workspace(project_root)


def clear_uv_workspace_cache() -> None:
    """Clear the UV workspace detection cache."""
    _uv_workspace_detector.clear_cache()
