"""Command registration and management module."""

import functools
from collections.abc import Callable
from typing import Any

from ..exceptions import CommandError
from .base import CommandBase
from .error_codes import ErrorCode
from .registry import (
    get_command,
    list_commands,
    register_alias,
    register_command,
    resolve_command_name,
)


class Command(CommandBase):
    """
    Base class for all commands.
    """

    def __init__(self, **dependencies: Any) -> None:
        super().__init__(**dependencies)

    @property
    def name(self) -> str:
        """
        Get the command name.

        Returns:
            str: The command name
        """
        raise NotImplementedError("Command subclasses must implement name property")

    @property
    def help(self) -> str:
        """
        Get the command help text.

        Returns:
            str: The command help text
        """
        raise NotImplementedError("Command subclasses must implement help property")

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """
        Execute the command.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        raise NotImplementedError("Command subclasses must implement execute method")

    def add_arguments(self, parser):
        """Default no-op arguments method to satisfy base requirements."""
        return None


def validate_command_args(**validators: Callable[[Any], bool]) -> Callable:
    """
    Decorator to validate command arguments.

    Args:
        **validators: A dictionary of argument names and validation functions

    Returns:
        Callable: The decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for arg_name, validator in validators.items():
                if arg_name in kwargs:
                    if not validator(kwargs[arg_name]):
                        raise ValueError(f"Invalid value for {arg_name}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = [
    "Command",
    "CommandBase",
    "ErrorCode",
    "get_command",
    "list_commands",
    "register_alias",
    "register_command",
    "resolve_command_name",
    "validate_command_args",
]
