from .. import Command as Command, register_command as register_command
from ...exceptions import CommandError as CommandError
from ...utils.logging import log_error as log_error
from .handlers.init_environment_handler import InitEnvironmentHandler as InitEnvironmentHandler
from .handlers.init_project_handler import InitProjectHandler as InitProjectHandler
from .handlers.init_work_handler import InitWorkHandler as InitWorkHandler
from .utils.exceptions import InitEnvError as InitEnvError
from typing import Any

class InitCommand(Command):
    def __init__(self) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def help(self) -> str: ...
    def add_arguments(self, parser) -> None: ...
    def execute(self, *args: Any, **kwargs: Any) -> None: ...
