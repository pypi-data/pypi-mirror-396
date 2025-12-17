from ...exceptions import CommandError as CommandError
from ...utils.logging import log_info as log_info
from ...utils.subprocess_utils import SubprocessExecutor as SubprocessExecutor

class PyPIUploader:
    def upload_to_pypi(self, repository: str, dist_files, username=None, password=None): ...
