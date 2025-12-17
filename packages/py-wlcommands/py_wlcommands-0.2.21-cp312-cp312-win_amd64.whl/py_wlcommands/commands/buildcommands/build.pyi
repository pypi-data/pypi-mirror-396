from .. import Command as Command, register_command as register_command
from .build_utils import build_project as build_project, build_project_full as build_project_full
from typing import Any

class BuildCommand(Command):
    @property
    def name(self) -> str: ...
    @property
    def help(self) -> str: ...
    def execute(self, *args: Any, **kwargs: Any) -> None: ...
