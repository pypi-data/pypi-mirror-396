"""Unified command base class for WL Commands."""

import argparse
from abc import ABC, abstractmethod
from typing import Any


class CommandBase(ABC):
    """
    Abstract base class for all commands, providing lifecycle and logging utilities.
    """

    def __init__(self, **dependencies: Any) -> None:
        self._dependencies = dependencies

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the command name."""
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Get the command help text."""
        pass

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments to the parser."""
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Execute the command."""
        pass

    def before_execute(self, *args: Any, **kwargs: Any) -> None:
        """Lifecycle hook called before execution."""
        return None

    def after_execute(self, result: Any = None) -> None:
        """Lifecycle hook called after execution."""
        return None

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run with lifecycle and error handling around execute."""
        try:
            # Validate arguments and use the validated kwargs
            validated_kwargs = self.validate_args(**kwargs)
            self.before_execute(*args, **validated_kwargs)
            result = self.execute(*args, **validated_kwargs)
            self.after_execute(result)
            return result
        except Exception as error:
            self.handle_error(error)
            raise

    def validate_args(self, **kwargs: Any) -> dict[str, Any]:
        """Validate command arguments."""
        return kwargs

    def handle_error(self, error: Exception) -> None:
        """Default error handler; override for custom behavior."""
        raise error

    def log_info(self, en_msg: str, zh_msg: str | None = None) -> None:
        """Log messages in English and optionally Chinese."""
        try:
            from py_wlcommands.utils.logging import log_info

            log_info(en_msg, lang="en")
            if zh_msg is not None:
                log_info(zh_msg, lang="zh")
        except Exception:
            # Logging utility may not be available in certain contexts; ignore
            pass


# Backward compatibility alias
BaseCommand = CommandBase
