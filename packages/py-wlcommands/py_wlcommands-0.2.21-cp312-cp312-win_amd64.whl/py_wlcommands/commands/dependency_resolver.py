"""Dependency resolution utilities for commands."""

from typing import Any, Dict

from ..infrastructure.dependency_injection import resolve


def resolve_dependencies(**annotations: Any) -> dict[str, Any]:
    """
    Resolve dependencies based on annotations using the dependency injection container.

    Args:
        **annotations: Annotations to resolve dependencies for

    Returns:
        Dict[str, Any]: A dictionary of dependency names and their instances
    """
    dependencies = {}
    for arg_name, _arg_type in annotations.items():
        try:
            dependencies[arg_name] = resolve(arg_name)
        except KeyError:
            # Dependency not found
            pass
    return dependencies
