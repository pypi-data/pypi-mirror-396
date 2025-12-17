"""
Log filtering utilities for WL Commands.
"""

from typing import Any


class LogFilter:
    """Filter logs based on context."""

    def __init__(self, **context) -> None:
        self.context = context

    def filter(self, record: dict[str, Any]) -> bool:
        """Filter log records based on context."""
        for key, value in self.context.items():
            if key in record and record[key] != value:
                return False
        return True
