"""Log filters for WL Commands."""

from typing import Any, Callable


class LogFilter:
    """Base class for log filters."""

    def __call__(self, record: dict[str, Any]) -> bool:
        """Determine if the log record should be processed."""
        raise NotImplementedError("Subclasses must implement __call__ method.")


class LevelFilter(LogFilter):
    """Filter logs based on log level."""

    def __init__(self, min_level: int, max_level: int | None = None) -> None:
        """
        Initialize level filter.

        Args:
            min_level (int): Minimum log level to include.
            max_level (Optional[int]): Maximum log level to include.
        """
        self.min_level = min_level
        self.max_level = max_level

    def __call__(self, record: dict[str, Any]) -> bool:
        """Check if log record level is within specified range."""
        level = record.get("level", 0)
        if level < self.min_level:
            return False
        if self.max_level is not None and level > self.max_level:
            return False
        return True


class KeyValueFilter(LogFilter):
    """Filter logs based on key-value pairs."""

    def __init__(self, **kwargs) -> None:
        """
        Initialize key-value filter.

        Args:
            **kwargs: Key-value pairs to match in log records.
        """
        self.filters = kwargs

    def __call__(self, record: dict[str, Any]) -> bool:
        """Check if log record contains all specified key-value pairs."""
        for key, value in self.filters.items():
            if record.get(key) != value:
                return False
        return True
