from ...exceptions import CommandError as CommandError
from ...utils.logging import log_info as log_info

class VersionUpdater:
    def increment_version(self, detector, comparator, pypi_checker=None, dry_run: bool = False) -> None: ...
