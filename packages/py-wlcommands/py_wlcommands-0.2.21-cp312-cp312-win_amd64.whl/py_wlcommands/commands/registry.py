"""Command registration and management module."""

from collections.abc import Callable
from typing import Any, Dict, Type

from .base import CommandBase
from .dependency_resolver import resolve_dependencies

# Command registry
_COMMANDS: dict[str, type[CommandBase]] = {}
_ALIASES: dict[str, str] = {}


# Define command modules with their paths for lazy importing
_COMMAND_MODULES = {
    "build": "buildcommands.build",
    "builddist": "buildcommands.dist",
    "buildtest": "buildcommands.test",
    "clean": "clean.clean",
    "config": "config.config",
    "format": "format.format_coordinator",
    "init": "initenv.initenv",
    "initenv": "initenv.initenv",
    "lint": "lint.lint_coordinator",
    "publish": "publish.publish",
    "self": "self.self_update",
    "test": "testcommands.test",
    "testcommands": "testcommands.test",  # Keep for backward compatibility
}


def register_command(name: str) -> Callable[[type[CommandBase]], type[CommandBase]]:
    """
    Decorator to register a command.

    Args:
        name (str): The name to register the command under

    Returns:
        Callable[[Type[Command]], Type[Command]]: The decorator function
    """

    def decorator(command_class: type[CommandBase]) -> type[CommandBase]:
        _COMMANDS[name] = command_class
        return command_class

    return decorator


def register_alias(alias: str, command_name: str) -> None:
    """
    Register an alias for a command.

    Args:
        alias (str): The alias to register
        command_name (str): The name of the command to alias
    """
    _ALIASES[alias] = command_name


def resolve_command_name(name: str) -> str:
    """
    Resolve a command name, handling aliases.

    Args:
        name (str): The command name or alias

    Returns:
        str: The resolved command name
    """
    return _ALIASES.get(name, name)


def list_commands() -> dict[str, type[CommandBase]]:
    """
    List all registered commands.

    Returns:
        Dict[str, Type[Command]]: A dictionary of command names and their classes
    """
    # Import all command modules to ensure all commands are registered
    for cmd_name, module_path in _COMMAND_MODULES.items():
        if cmd_name not in _COMMANDS:
            _import_command_module(module_path)
    return _COMMANDS.copy()


def get_command(name: str) -> CommandBase:
    """
    Get an instance of a registered command.

    Args:
        name (str): The name of the command to get

    Returns:
        Command: An instance of the requested command

    Raises:
        ValueError: If the command is not found
    """
    resolved_name = resolve_command_name(name)

    # If command is not registered yet, try to import its module
    if resolved_name not in _COMMANDS:
        if resolved_name in _COMMAND_MODULES:
            _import_command_module(_COMMAND_MODULES[resolved_name])
        else:
            # Check if alias points to a known command with module
            if resolved_name in _ALIASES:
                original_name = _ALIASES[resolved_name]
                if original_name in _COMMAND_MODULES:
                    _import_command_module(_COMMAND_MODULES[original_name])

    if resolved_name not in _COMMANDS:
        raise ValueError(f"Command '{name}' not found")

    command_class = _COMMANDS[resolved_name]
    dependencies = resolve_dependencies(**command_class.__init__.__annotations__)
    return command_class(**dependencies)


def _import_command_module(module_path):
    """Import a command module dynamically."""
    import importlib

    # Construct the full module path
    full_module_path = f"py_wlcommands.commands.{module_path}"

    try:
        # Import the full module path
        importlib.import_module(full_module_path)
    except ImportError as e:
        # Try importing just the base module (for directories like buildcommands)
        base_module_path = f"py_wlcommands.commands.{module_path.split('.')[0]}"
        try:
            importlib.import_module(base_module_path)
        except ImportError:
            # If still failing, just log and continue - this allows commands
            # that don't need certain modules to still work
            import logging

            logging.debug(
                f"Failed to import {full_module_path} or {base_module_path}: {e}"
            )


# Register common aliases
register_alias("i", "init")
register_alias("b", "build")
register_alias("t", "test")  # Added test alias
register_alias("f", "format")
register_alias("l", "lint")
register_alias("c", "clean")
