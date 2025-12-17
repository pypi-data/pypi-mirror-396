"""Version comparison and validation utilities."""


class VersionComparator:
    """Handle version comparison and validation operations."""

    @staticmethod
    def is_version_increment_valid(old_version: str, new_version: str) -> bool:
        """
        Check if the new version is a valid increment from the old version.
        Allows:
        1. Incrementing patch version by 1 (e.g., 0.1.5 -> 0.1.6).
        2. Incrementing minor version by 1 and resetting patch to 0 (e.g., 0.1.5 -> 0.2.0).
        3. Incrementing major version by 1 and resetting minor and patch to 0 (e.g., 0.1.5 -> 1.0.0).
        4. New version being greater than old version (for cases where local version is behind PyPI).
        5. New version being equal to old version (to trigger auto-increment).
        """
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
        except (ValueError, AttributeError):
            # If any error occurs during parsing, consider it invalid
            return False

    @staticmethod
    def get_greater_version(version1: str, version2: str) -> str:
        """Return the greater of two version strings."""
        try:
            v1_parts: list[int] = list(map(int, version1.split(".")))
            v2_parts: list[int] = list(map(int, version2.split(".")))

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
        except (ValueError, IndexError):
            # If comparison fails, return the first version as default
            return version1

    @staticmethod
    def is_version_greater(version1: str, version2: str) -> bool:
        """Check if version1 is greater than version2."""
        try:
            v1_parts: list[int] = list(map(int, version1.split(".")))
            v2_parts: list[int] = list(map(int, version2.split(".")))

            # Compare major version
            if v1_parts[0] > v2_parts[0]:
                return True
            elif v1_parts[0] < v2_parts[0]:
                return False

            # Compare minor version
            if v1_parts[1] > v2_parts[1]:
                return True
            elif v1_parts[1] < v2_parts[1]:
                return False

            # Compare patch version
            if v1_parts[2] > v2_parts[2]:
                return True
            else:
                return False
        except (ValueError, IndexError):
            # If comparison fails, assume version1 is not greater
            return False

    @staticmethod
    def increment_version_from_base(base_version: str) -> str:
        """Increment version by patch number from a base version."""
        try:
            version_parts = list(map(int, base_version.split(".")))
            # Must have exactly 3 parts
            if len(version_parts) != 3:
                raise ValueError(f"Version must have exactly 3 parts: {base_version}")
            # Increment patch version
            version_parts[2] += 1
            new_version = ".".join(map(str, version_parts))
            return new_version
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to increment version {base_version}: {e}")
