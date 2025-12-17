from ...exceptions import CommandError as CommandError
from ..logging import log_info as log_info
from .pypi_version_checker import PyPIVersionChecker as PyPIVersionChecker
from .version_comparator import VersionComparator as VersionComparator
from .version_detectors import VersionDetector as VersionDetector
from .version_updater import VersionUpdater as VersionUpdater
from _typeshed import Incomplete
from types import ModuleType

aiohttp: ModuleType | None
ClientError: type[Exception]

class VersionService:
    comparator: Incomplete
    detector: Incomplete
    pypi_checker: Incomplete
    updater: Incomplete
    def __init__(self) -> None: ...
    def get_current_version(self) -> str: ...
    def check_version_with_pypi(self, repository: str, current_version: str) -> None: ...
    async def check_version_with_pypi_async(self, repository: str, current_version: str) -> None: ...
    def increment_version(self, dry_run: bool = False): ...
    async def increment_version_async(self, dry_run: bool = False) -> None: ...
