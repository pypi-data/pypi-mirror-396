from ..log_levels import LogLevel as LogLevel
from ..log_rotators import LogRotator as LogRotator
from .formatters import LogFormatter as LogFormatter
from .handlers import LogHandler as LogHandler
from _typeshed import Incomplete
from typing import Any, Callable

class StructuredLogger:
    name: Incomplete
    min_level: Incomplete
    log_file: Incomplete
    filters: list[Callable[[dict[str, Any]], bool]]
    log_rotator: Incomplete
    enable_console: Incomplete
    console_format: Incomplete
    log_file_format: Incomplete
    formatter: Incomplete
    handler: Incomplete
    def __init__(self, name: str, min_level: int | None = None, log_file: str | None = None) -> None: ...
    def add_filter(self, filter_func) -> None: ...
    def debug(self, message: str, **kwargs) -> None: ...
    def info(self, message: str, **kwargs) -> None: ...
    def warning(self, message: str, **kwargs) -> None: ...
    def error(self, message: str, **kwargs) -> None: ...
    def critical(self, message: str, **kwargs) -> None: ...
