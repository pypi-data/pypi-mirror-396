from ..log_rotators import LogRotator as LogRotator
from .formatters import LogFormatter as LogFormatter
from _typeshed import Incomplete
from typing import Any

class LogHandler:
    log_file: Incomplete
    log_rotator: Incomplete
    enable_console: Incomplete
    console_format: Incomplete
    log_file_format: Incomplete
    formatter: Incomplete
    def __init__(self, log_file: str | None, log_rotator: LogRotator | None, enable_console: bool, console_format: str, log_file_format: str) -> None: ...
    def write_log(self, record: dict[str, Any]) -> None: ...
