"""Log handlers for WL Commands."""

import json
import sys
from typing import Any

from ..log_rotators import LogRotator
from .formatters import LogFormatter


class LogHandler:
    """Handles writing log messages to various outputs."""

    def __init__(
        self,
        log_file: str | None,
        log_rotator: LogRotator | None,
        enable_console: bool,
        console_format: str,
        log_file_format: str,
    ) -> None:
        """
        Initialize log handler.

        Args:
            log_file (Optional[str]): Path to log file.
            log_rotator (Optional[LogRotator]): Log rotator instance.
            enable_console (bool): Whether to enable console output.
            console_format (str): Console output format ('colored' or 'json').
            log_file_format (str): Log file format ('human' or 'json').
        """
        self.log_file = log_file
        self.log_rotator = log_rotator
        self.enable_console = enable_console
        self.console_format = console_format
        self.log_file_format = log_file_format
        self.formatter = LogFormatter()

    def write_log(self, record: dict[str, Any]) -> None:
        """Write log record to appropriate outputs."""
        # Convert record to JSON string first
        json_message = self.formatter.format_json_log(record)

        # Process log message for file output based on format
        file_message = json_message
        if self.log_file and self.log_file_format == "human":
            try:
                # Parse JSON message and reformat as human-readable
                log_record = json.loads(json_message)
                file_message = self.formatter.format_human_log(log_record)
            except (json.JSONDecodeError, TypeError):
                # Fallback to raw message if parsing fails
                pass

        # Write to file if specified
        if self.log_file and self.log_rotator:
            # Handle log rotation
            if self.log_rotator.should_rotate():
                self.log_rotator.do_rotate()

            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(file_message + "\n")
            except OSError:
                # Ignore file write errors
                pass

        # Write to console only if enabled
        if self.enable_console:
            if self.console_format == "colored":
                # Beautify for console with colors
                try:
                    log_record = json.loads(json_message)
                    # Format console output with colors
                    console_message = self.formatter.format_console_log(log_record)
                except (json.JSONDecodeError, TypeError):
                    # Fallback to raw message if parsing fails
                    console_message = json_message
            else:
                # Use raw JSON format for console
                console_message = json_message

            target = (
                sys.stdout
                if "ERROR" not in json_message and "CRITICAL" not in json_message
                else sys.stderr
            )
            try:
                print(console_message, file=target)
            except OSError:
                # Ignore console write errors
                pass
