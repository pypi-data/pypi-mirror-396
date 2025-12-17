from _typeshed import Incomplete
from py_wlcommands.utils.logging import log_error as log_error, log_info as log_info

class GitLFSManager:
    env: Incomplete
    three_d_file_types: Incomplete
    def __init__(self, env: dict[str, str]) -> None: ...
    def initialize(self) -> None: ...
