"""Log manager utility for initenv module."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from ....utils.log_levels import LogLevel
from ....utils.logging import (
    StructuredLogger,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
)


class LogManager:
    """Manager for logging with levels - now using unified logging system."""

    def __init__(self, name: str = "initenv") -> None:
        self.logger: StructuredLogger = get_logger(name)

    def set_level(self, level: int) -> None:
        """Set logging level."""
        # Map standard logging levels to our LogLevel constants
        level_map = {
            10: LogLevel.DEBUG,  # logging.DEBUG
            20: LogLevel.INFO,  # logging.INFO
            30: LogLevel.WARNING,  # logging.WARNING
            40: LogLevel.ERROR,  # logging.ERROR
            50: LogLevel.CRITICAL,  # logging.CRITICAL
        }
        self.logger.min_level = level_map.get(level, LogLevel.INFO)

    def info(self, message: str, lang: str = "en") -> None:
        """Log info message."""
        log_info(message, lang=lang)

    def warning(self, message: str) -> None:
        """Log warning message."""
        log_warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        log_error(message)

    def debug(self, message: str) -> None:
        """Log debug message."""
        log_debug(message)


def performance_monitor(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to monitor function execution time."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        log_info(f"Starting {func.__name__}...")
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        log_info(
            f"Finished {func.__name__} in {execution_time:.2f} seconds",
            duration=execution_time,
        )
        return result

    return wrapper
