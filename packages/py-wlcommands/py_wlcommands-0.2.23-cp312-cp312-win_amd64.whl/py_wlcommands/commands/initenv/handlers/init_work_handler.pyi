from py_wlcommands.commands.initenv.utils.git_initializer import GitInitializer as GitInitializer
from py_wlcommands.commands.initenv.utils.platform_adapter import PlatformAdapter as PlatformAdapter
from py_wlcommands.utils.logging import log_info as log_info

class InitWorkHandler:
    @staticmethod
    def initialize(work_type: str) -> None: ...

class CommitFormatGuide:
    @staticmethod
    def show() -> None: ...
