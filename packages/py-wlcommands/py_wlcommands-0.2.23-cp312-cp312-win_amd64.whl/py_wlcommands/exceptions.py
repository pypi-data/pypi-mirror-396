"""
Custom exceptions for WL Commands.
"""


class ErrorCode:
    """Standard error codes."""

    SUCCESS = 0
    COMMAND_NOT_FOUND = 1
    COMMAND_EXECUTION_FAILED = 2
    INVALID_ARGUMENT = 3
    MISSING_DEPENDENCY = 4
    MAKE_NOT_FOUND = 5
    UV_NOT_FOUND = 6


class CommandError(Exception):
    """Base exception for command failures."""

    def __init__(
        self, message: str, error_code: int = ErrorCode.COMMAND_EXECUTION_FAILED
    ) -> None:
        """
        Initialize command error.

        Args:
            message (str): Error message.
            error_code (int): Error code.
        """
        super().__init__(message)
        self.error_code = error_code


class MakeNotFoundError(CommandError):
    """Raised when 'make' command is not found."""

    def __init__(self, message: str = "Make command not found") -> None:
        super().__init__(message, ErrorCode.MAKE_NOT_FOUND)


class UVNotFoundError(CommandError):
    """Raised when 'uv' command is not found."""

    def __init__(self, message: str = "UV command not found") -> None:
        super().__init__(message, ErrorCode.UV_NOT_FOUND)
