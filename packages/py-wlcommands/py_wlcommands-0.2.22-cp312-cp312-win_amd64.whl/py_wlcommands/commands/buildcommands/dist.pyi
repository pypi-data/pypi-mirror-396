from .. import Command as Command, register_command as register_command
from ...exceptions import CommandError as CommandError
from ...utils.logging import log_error as log_error, log_info as log_info
from ...utils.uv_workspace import is_uv_workspace as is_uv_workspace
from ...utils.workspace_detector import WorkspaceDetectionError as WorkspaceDetectionError, WorkspaceDetector as WorkspaceDetector
from ..format.python_formatter import generate_type_stubs as generate_type_stubs
from typing import Any

class BuildDistCommand(Command):
    @property
    def name(self) -> str: ...
    @property
    def help(self) -> str: ...
    def add_arguments(self, parser) -> None: ...
    def execute(self, *args: Any, **kwargs: Any) -> None: ...
