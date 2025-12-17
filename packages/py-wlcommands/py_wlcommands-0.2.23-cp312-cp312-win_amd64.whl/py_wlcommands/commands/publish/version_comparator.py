"""Version comparison and validation utilities."""


class VersionComparator:
    """Handle version comparison and validation operations."""

    @staticmethod
    def is_version_increment_valid(
        old_version: str | None, new_version: str | None
    ) -> bool:
        """
        Check if the new version is a valid increment from the old version.
        Allows:
        1. Incrementing patch version by 1 (e.g., 0.1.5 -> 0.1.6).
        2. Incrementing minor version by 1 and resetting patch to 0 (e.g., 0.1.5 -> 0.2.0).
        3. Incrementing major version by 1 and resetting minor and patch to 0 (e.g., 0.1.5 -> 1.0.0).
        4. New version being greater than old version (for cases where local version is behind PyPI).
        5. New version being equal to old version (to trigger auto-increment).
        """
        # Validate inputs are not None before proceeding
        if old_version is None or new_version is None:
            return False

        try:
            old_parts = list(map(int, old_version.split(".")))
            new_parts = list(map(int, new_version.split(".")))

            # Must have exactly 3 parts
            if len(old_parts) != 3 or len(new_parts) != 3:
                return False

            # If new version is less than old version, it's invalid
            if new_parts[0] < old_parts[0]:
                return False
            elif new_parts[0] == old_parts[0]:
                if new_parts[1] < old_parts[1]:
                    return False
                elif new_parts[1] == old_parts[1]:
                    if new_parts[2] < old_parts[2]:
                        # New version must be greater than or equal to old version
                        return False
                # else new_parts[1] > old_parts[1], which is valid

            # All other cases are valid (new version is greater than or equal to old version)
            return True
        except (ValueError, AttributeError, TypeError):
            # If any error occurs during parsing or None values are provided, consider it invalid
            return False

    @staticmethod
    def get_greater_version(version1: str | None, version2: str | None) -> str | None:
        """Return the greater of two version strings."""
        # Handle None values as per test expectations
        if version1 is None:
            return None
        if version2 is None:
            return version1

        try:
            # Split and pad versions to ensure at least 3 parts
            v1_parts: list[int] = list(map(int, version1.split(".")))
            v2_parts: list[int] = list(map(int, version2.split(".")))

            # Pad with zeros to ensure we have at least 3 parts
            v1_parts.extend([0] * (3 - len(v1_parts)))
            v2_parts.extend([0] * (3 - len(v2_parts)))

            # Compare major version
            if v1_parts[0] > v2_parts[0]:
                return version1
            elif v1_parts[0] < v2_parts[0]:
                return version2

            # Compare minor version
            if v1_parts[1] > v2_parts[1]:
                return version1
            elif v1_parts[1] < v2_parts[1]:
                return version2

            # Compare patch version
            if v1_parts[2] > v2_parts[2]:
                return version1
            elif v1_parts[2] < v2_parts[2]:
                return version2

            # Versions are equal, return either one
            return version1
        except (ValueError, TypeError):
            # If comparison fails, return the first version as default
            return version1

    @staticmethod
    def increment_version_from_base(base_version: str) -> str:
        """Increment version by patch number from a base version."""
        try:
            version_parts = list(map(int, base_version.split(".")))
            # Increment patch version
            version_parts[2] += 1
            new_version = ".".join(map(str, version_parts))
            return new_version
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to increment version {base_version}: {e}")
