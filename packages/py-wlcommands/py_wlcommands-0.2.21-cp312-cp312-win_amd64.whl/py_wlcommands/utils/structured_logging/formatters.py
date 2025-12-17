"""Log formatters for WL Commands."""

import datetime
import json
import sys
from typing import Any


class LogFormatter:
    """Handles formatting of log messages."""

    # ANSI color codes for console output
    _COLORS = {
        "DEBUG": "\033[34m",  # Blue
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[91m",  # Bright Red
        "RESET": "\033[0m",  # Reset color
        "TIMESTAMP": "\033[90m",  # Gray for timestamp
        "LOGGER": "\033[36m",  # Cyan for logger name
    }

    def format_human_log(self, record: dict[str, Any]) -> str:
        """Format log record for human-readable file output without colors."""
        # Extract log fields
        level_name = record.get("level_name", "UNKNOWN")
        logger_name = record.get("logger_name", "unknown")
        message = record.get("message", "")
        timestamp = record.get("timestamp", "")

        # Format timestamp for better readability
        if timestamp:
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                formatted_time = timestamp
        else:
            formatted_time = ""

        # Build human-readable log message (similar to console format but without colors)
        # Format: [2025-12-12 20:36:01] INFO test_logger - Test log message
        human_log = f"[{formatted_time}] {level_name} {logger_name} - {message}"

        return human_log

    def format_console_log(self, record: dict[str, Any]) -> str:
        """Format log record for console output with colors and readable format."""
        # Extract log fields
        level_name = record.get("level_name", "UNKNOWN")
        logger_name = record.get("logger_name", "unknown")
        message = record.get("message", "")
        timestamp = record.get("timestamp", "")

        # Format timestamp for better readability (YYYY-MM-DD HH:MM:SS)
        if timestamp:
            try:
                # Parse ISO format timestamp
                dt = datetime.datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Fallback to original timestamp if parsing fails
                formatted_time = timestamp
        else:
            formatted_time = ""

        # Get color codes
        color = self._COLORS.get(level_name, self._COLORS["RESET"])
        reset = self._COLORS["RESET"]
        timestamp_color = self._COLORS["TIMESTAMP"]
        logger_color = self._COLORS["LOGGER"]

        # Build console log message
        # Format: [2025-12-12 19:53:58] INFO wl - features 分支已存在
        console_log = f"{timestamp_color}[{formatted_time}]{reset} {color}{level_name}{reset} {logger_color}{logger_name}{reset} - {message}"

        return console_log

    def format_json_log(self, record: dict[str, Any]) -> str:
        """Format log record as JSON."""
        try:
            return json.dumps(record)
        except (TypeError, ValueError):
            # Fallback if JSON serialization fails
            simple_record = {
                "logger_name": record.get("logger_name", "unknown"),
                "level": record.get("level", 0),
                "level_name": record.get("level_name", "UNKNOWN"),
                "timestamp": record.get("timestamp", ""),
                "message": record.get("message", ""),
            }
            return json.dumps(simple_record)
