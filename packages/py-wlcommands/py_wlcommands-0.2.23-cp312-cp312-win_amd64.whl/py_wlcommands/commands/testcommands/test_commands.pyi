from .. import register_command as register_command
from ...utils.logging import log_info as log_info
from ...utils.project_root import find_project_root as find_project_root
from ..base import BaseCommand as BaseCommand
from .python_env_detector import PythonEnvDetector as PythonEnvDetector
from .test_command_builder import TestCommandBuilder as TestCommandBuilder
from .test_result_handler import TestResultHandler as TestResultHandler
from _typeshed import Incomplete
from typing import Any

class TestCommand(BaseCommand):
    __test__: bool
    python_detector: Incomplete
    command_builder: Incomplete
    result_handler: Incomplete
    def __init__(self) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def help(self) -> str: ...
    def add_arguments(self, parser) -> None: ...
    def execute(self, *args: Any, **kwargs: Any) -> None: ...
