"""Version management for publish command."""

# Import new VersionService from utils
from ...utils.version import VersionService


class VersionManager:
    """Manage version operations for the publish command."""

    def __init__(self):
        """Initialize version manager with component handlers."""
        # Use the new VersionService from utils
        self.version_service = VersionService()

    def get_current_version(self) -> str:
        """Get the current version from Cargo.toml or __init__.py."""
        return self.version_service.get_current_version()

    def check_version_with_pypi(self, repository: str, current_version: str) -> None:
        """Check the current version against PyPI to ensure proper versioning."""
        self.version_service.check_version_with_pypi(repository, current_version)

    def increment_version(self, dry_run: bool = False) -> None:
        """Increment the version to be greater than both local and PyPI versions."""
        self.version_service.increment_version(dry_run)
