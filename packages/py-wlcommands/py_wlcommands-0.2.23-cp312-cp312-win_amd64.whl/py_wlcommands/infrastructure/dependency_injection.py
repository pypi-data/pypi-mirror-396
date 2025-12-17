"""Dependency injection container for WL Commands."""

import threading
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class DependencyInjectionContainer:
    """A dependency injection container for managing dependencies."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the dependency injection container."""
        if not hasattr(self, "_initialized"):
            self._singletons: dict[str, Any] = {}
            self._factories: dict[str, Callable[[], Any]] = {}
            self._instances: dict[str, Any] = {}
            self._initialized = True
            # Register common infrastructure classes as singletons
            self._register_default_singletons()

    def _register_default_singletons(self) -> None:
        """Register default singleton dependencies."""
        # 延迟导入以避免循环导入
        from ..utils.file_operations import FileOperations
        from ..utils.performance_monitor import PerformanceMonitor
        from ..utils.subprocess_utils import SubprocessExecutor

        self.register_singleton("FileOperations", FileOperations)
        self.register_singleton("SubprocessExecutor", SubprocessExecutor)
        self.register_singleton("PerformanceMonitor", PerformanceMonitor)

    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a singleton dependency.

        Args:
            name: The name of the dependency
            factory: A factory function that creates the dependency
        """
        self._factories[name] = factory

    def register_transient(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a transient dependency (new instance each time).

        Args:
            name: The name of the dependency
            factory: A factory function that creates the dependency
        """
        self._factories[name] = factory

    def register_instance(self, name: str, instance: Any) -> None:
        """
        Register a specific instance.

        Args:
            name: The name of the dependency
            instance: The instance to register
        """
        self._instances[name] = instance

    def resolve(self, name: str) -> Any:
        """
        Resolve a dependency by name.

        Args:
            name: The name of the dependency to resolve

        Returns:
            The resolved dependency

        Raises:
            KeyError: If the dependency is not registered
        """
        # First check for specific instances
        if name in self._instances:
            return self._instances[name]

        # Then check for singletons
        if name in self._singletons:
            return self._singletons[name]

        # Create new instance using factory
        if name in self._factories:
            instance = self._factories[name]()
            # If it's a singleton, store it for future use
            # In this simple implementation, we treat all registered factories as singletons
            self._singletons[name] = instance
            return instance

        raise KeyError(f"Dependency '{name}' not registered")

    def resolve_by_type(self, type_: type[T]) -> T:
        """
        Resolve a dependency by type.

        Args:
            type_: The type of the dependency to resolve

        Returns:
            The resolved dependency
        """
        # Try to resolve by type name
        return self.resolve(type_.__name__)

    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._singletons.clear()
        self._factories.clear()
        self._instances.clear()


# Global container instance
_container = DependencyInjectionContainer()


def get_container() -> DependencyInjectionContainer:
    """
    Get the global dependency injection container.

    Returns:
        The global dependency injection container
    """
    return _container


def register_singleton(name: str, factory: Callable[[], Any]) -> None:
    """
    Register a singleton dependency in the global container.

    Args:
        name: The name of the dependency
        factory: A factory function that creates the dependency
    """
    _container.register_singleton(name, factory)


def register_transient(name: str, factory: Callable[[], Any]) -> None:
    """
    Register a transient dependency in the global container.

    Args:
        name: The name of the dependency
        factory: A factory function that creates the dependency
    """
    _container.register_transient(name, factory)


def register_instance(name: str, instance: Any) -> None:
    """
    Register a specific instance in the global container.

    Args:
        name: The name of the dependency
        instance: The instance to register
    """
    _container.register_instance(name, instance)


def resolve(name: str) -> Any:
    """
    Resolve a dependency by name from the global container.

    Args:
        name: The name of the dependency to resolve

    Returns:
        The resolved dependency
    """
    return _container.resolve(name)


def resolve_by_type(type_: type[T]) -> T:
    """
    Resolve a dependency by type from the global container.

    Args:
        type_: The type of the dependency to resolve

    Returns:
        The resolved dependency
    """
    return _container.resolve_by_type(type_)
