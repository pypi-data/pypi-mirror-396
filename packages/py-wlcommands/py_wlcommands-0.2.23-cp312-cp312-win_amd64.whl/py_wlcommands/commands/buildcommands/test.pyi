from .. import Command as Command, register_command as register_command
from ...exceptions import CommandError as CommandError
from ...utils.logging import log_error as log_error, log_info as log_info
from ...utils.subprocess import run_command as run_command
from typing import Any

class BuildTestCommand(Command):
    @property
    def name(self) -> str: ...
    @property
    def help(self) -> str: ...
    def execute(self, *args: Any, **kwargs: Any) -> None: ...
