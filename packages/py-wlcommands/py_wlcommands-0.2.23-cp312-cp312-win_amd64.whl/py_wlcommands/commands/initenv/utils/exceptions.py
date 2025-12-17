"""Custom exceptions for initenv module."""

from ....exceptions import CommandError


class InitEnvError(CommandError):
    """Base exception for initenv module."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class GitInitializationError(InitEnvError):
    """Git initialization exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PyProjectGenerationError(InitEnvError):
    """PyProject.toml generation exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProjectStructureSetupError(InitEnvError):
    """Project structure setup exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class RustInitializationError(InitEnvError):
    """Rust environment initialization exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VenvCreationError(InitEnvError):
    """Virtual environment creation exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
