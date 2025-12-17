from py_wlcommands.commands.initenv.utils.platform_adapter import PlatformAdapter as PlatformAdapter
from py_wlcommands.commands.initenv.utils.project_structure import ProjectStructureSetup as ProjectStructureSetup
from py_wlcommands.utils.logging import log_error as log_error, log_info as log_info

class InitProjectHandler:
    @staticmethod
    def initialize() -> None: ...
