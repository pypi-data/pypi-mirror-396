from py_wlcommands.commands.initenv.utils.initializer import Initializer as Initializer
from py_wlcommands.commands.initenv.utils.platform_adapter import PlatformAdapter as PlatformAdapter
from py_wlcommands.utils.logging import log_info as log_info

class InitEnvironmentHandler:
    @staticmethod
    def initialize(**kwargs) -> None: ...
