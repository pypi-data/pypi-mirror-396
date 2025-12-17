"""Logging utilities for WL Commands."""

import inspect
import sys
from functools import partial
from typing import Any

# Import modular components
from .language_utils import _should_display_language
from .log_levels import LogLevel
from .structured_logger import StructuredLogger

# Create a default structured logger (console output controlled by config)
default_logger = StructuredLogger("wl")


# Enhanced logging functions that use the structured logger
# while maintaining backward compatibility
def log_debug(message: str, **kwargs) -> None:
    """
    Log a debug message.

    Args:
        message (str): Message to log.
        **kwargs: Additional context for the log message.
    """
    # Add caller information for debug logs
    caller_frame = inspect.currentframe().f_back
    if caller_frame:
        caller_info = inspect.getframeinfo(caller_frame)
        kwargs.update(
            {
                "module": caller_info.filename.split("/")[-1].split(".")[0],
                "function": caller_info.function,
                "line": caller_info.lineno,
            }
        )
    default_logger.debug(message, **kwargs)


def log_info(message: str, lang: str = "en", **kwargs) -> None:
    """
    Log an informational message.

    Args:
        message (str): Message to log.
        lang (str, optional): Language of the message. Defaults to "en".
        **kwargs: Additional context for the log message.
    """
    # Use structured logging
    default_logger.info(message, lang=lang, **kwargs)

    # Maintain backward compatibility for console output
    if _should_display_language(lang):
        try:
            if lang == "en":
                print(f"INFO: {message}")
            elif lang == "zh":
                print(f"信息: {message}")
        except OSError:
            # Ignore print errors
            pass


def log_warning(message: str, lang: str = "en", **kwargs) -> None:
    """
    Log a warning message.

    Args:
        message (str): Message to log.
        lang (str, optional): Language of the message. Defaults to "en".
        **kwargs: Additional context for the log message.
    """
    # Use structured logging
    default_logger.warning(message, lang=lang, **kwargs)

    # Maintain backward compatibility for console output
    if _should_display_language(lang):
        try:
            if lang == "en":
                print(f"WARNING: {message}", file=sys.stderr)
            elif lang == "zh":
                print(f"警告: {message}", file=sys.stderr)
        except OSError:
            # Ignore print errors
            pass


def log_error(message: str, lang: str = "en", **kwargs) -> None:
    """
    Log an error message.

    Args:
        message (str): Message to log.
        lang (str, optional): Language of the message. Defaults to "en".
        **kwargs: Additional context for the log message.
    """
    # Add caller information for error logs
    caller_frame = inspect.currentframe().f_back
    if caller_frame:
        caller_info = inspect.getframeinfo(caller_frame)
        kwargs.update(
            {
                "module": caller_info.filename.split("/").pop().split(".")[0],
                "function": caller_info.function,
                "line": caller_info.lineno,
            }
        )

    # Use structured logging
    default_logger.error(message, lang=lang, **kwargs)

    # Maintain backward compatibility for console output
    if _should_display_language(lang):
        try:
            if lang == "en":
                print(f"ERROR: {message}", file=sys.stderr)
            elif lang == "zh":
                print(f"错误: {message}", file=sys.stderr)
        except OSError:
            # Ignore print errors
            pass


def log_critical(message: str, lang: str = "en", **kwargs) -> None:
    """
    Log a critical message.

    Args:
        message (str): Message to log.
        lang (str, optional): Language of the message. Defaults to "en".
        **kwargs: Additional context for the log message.
    """
    # Add caller information for critical logs
    caller_frame = inspect.currentframe().f_back
    if caller_frame:
        caller_info = inspect.getframeinfo(caller_frame)
        kwargs.update(
            {
                "module": caller_info.filename.split("/").pop().split(".")[0],
                "function": caller_info.function,
                "line": caller_info.lineno,
            }
        )

    # Use structured logging
    default_logger.critical(message, lang=lang, **kwargs)

    # Maintain backward compatibility for console output
    if _should_display_language(lang):
        try:
            if lang == "en":
                print(f"CRITICAL: {message}", file=sys.stderr)
            elif lang == "zh":
                print(f"严重: {message}", file=sys.stderr)
        except OSError:
            # Ignore print errors
            pass


# Alias for backward compatibility
log_info_structured = log_info


# Convenience function to get a logger instance
def get_logger(name: str = "wl") -> StructuredLogger:
    """
    Get a logger instance with the specified name.

    Args:
        name (str, optional): Logger name. Defaults to "wl".

    Returns:
        StructuredLogger: Logger instance.
    """
    return StructuredLogger(name)
