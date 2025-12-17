"""Unified error handling utilities for WL Commands."""

from ..exceptions import CommandError


class ErrorHandler:
    """Unified error handler for WL Commands."""

    @staticmethod
    def handle_error(error: Exception, context: str | None = None) -> None:
        """
        Handle an error with consistent formatting.

        Args:
            error: The exception to handle
            context: Optional context information about where the error occurred
        """
        error_type = type(error).__name__
        error_message = str(error)

        if context:
            print(f"Error in {context}: {error_type} - {error_message}")
        else:
            print(f"{error_type}: {error_message}")

        # For debugging purposes, we can optionally print the full traceback
        # This should be controlled by a verbosity setting in a real implementation
        # traceback.print_exc()

    @staticmethod
    def wrap_command_execution(func, *args, **kwargs):
        """
        Wrap command execution with error handling.

        Args:
            func: The function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function execution

        Raises:
            CommandError: If the function raises an exception
        """
        try:
            return func(*args, **kwargs)
        except CommandError:
            # Re-raise CommandError as is
            raise
        except Exception as e:
            # Wrap other exceptions in CommandError
            raise CommandError(f"Command execution failed: {str(e)}") from e


class ErrorContext:
    """Context manager for error handling."""

    def __init__(self, context: str):
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            ErrorHandler.handle_error(exc_val, self.context)
            return True  # Suppress the exception
        return False
