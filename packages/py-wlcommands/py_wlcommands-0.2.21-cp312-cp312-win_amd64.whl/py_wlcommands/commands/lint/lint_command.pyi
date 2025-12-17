from ...utils.logging import log_info as log_info
from ...utils.project_root import find_project_root as find_project_root
from ...utils.subprocess_utils import SubprocessResult as SubprocessResult
from .lint_executor import LintExecutor as LintExecutor
from .lint_formatter import LintFormatter as LintFormatter
from .lint_reporter import LintReporter as LintReporter
from _typeshed import Incomplete
from argparse import ArgumentParser

class LintCommandImpl:
    executor: Incomplete
    formatter: Incomplete
    reporter: Incomplete
    def __init__(self) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def help(self) -> str: ...
    def add_arguments(self, parser: ArgumentParser) -> None: ...
    def execute(self, paths: list[str] | None = None, quiet: bool = False, fix: bool = False, noreport: bool = False, report: bool = False, **kwargs: dict[str, object]) -> None: ...
