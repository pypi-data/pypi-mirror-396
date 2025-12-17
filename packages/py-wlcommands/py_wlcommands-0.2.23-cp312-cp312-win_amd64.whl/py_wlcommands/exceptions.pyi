from _typeshed import Incomplete

class ErrorCode:
    SUCCESS: int
    COMMAND_NOT_FOUND: int
    COMMAND_EXECUTION_FAILED: int
    INVALID_ARGUMENT: int
    MISSING_DEPENDENCY: int
    MAKE_NOT_FOUND: int
    UV_NOT_FOUND: int

class CommandError(Exception):
    error_code: Incomplete
    def __init__(self, message: str, error_code: int = ...) -> None: ...

class MakeNotFoundError(CommandError):
    def __init__(self, message: str = 'Make command not found') -> None: ...

class UVNotFoundError(CommandError):
    def __init__(self, message: str = 'UV command not found') -> None: ...
