from ...exceptions import CommandError as CommandError

class VersionDetector:
    def get_current_version(self, comparator) -> str: ...
