from ...exceptions import CommandError as CommandError
from ...utils.logging import log_info as log_info

class PyPIVersionChecker:
    def check_version_with_pypi(self, repository: str, current_version: str, comparator) -> None: ...
