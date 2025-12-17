"""
Log rotation utilities for WL Commands.
"""

import os
import time
from datetime import datetime, timedelta


class LogRotator:
    """Enhanced log rotator that supports size-based and time-based rotation."""

    def __init__(
        self,
        filename: str,
        max_size: int = 10 * 1024 * 1024,  # 10MB default
        max_backups: int = 5,  # Keep up to 5 backup files
        rotate_days: int = 7,  # Rotate after 7 days
    ) -> None:
        """
        Initialize log rotator.

        Args:
            filename (str): Log file name.
            max_size (int): Maximum file size in bytes before rotation.
            max_backups (int): Maximum number of backup files to keep.
            rotate_days (int): Number of days before rotating the log file.
        """
        self.filename = filename
        self.max_size = max_size
        self.max_backups = max_backups
        self.rotate_days = rotate_days

    def should_rotate(self) -> bool:
        """Check if log file should be rotated based on size or time."""
        try:
            if not os.path.exists(self.filename):
                return False

            # Check size-based rotation
            if os.path.getsize(self.filename) >= self.max_size:
                return True

            # Check time-based rotation
            file_mtime = os.path.getmtime(self.filename)
            if time.time() - file_mtime >= self.rotate_days * 24 * 60 * 60:
                return True

            return False
        except OSError:
            return False

    def do_rotate(self) -> None:
        """Perform log rotation with multiple backup files."""
        try:
            if not os.path.exists(self.filename):
                return

            # Rotate existing backups
            for i in range(self.max_backups - 1, 0, -1):
                old_backup = f"{self.filename}.{i}"
                new_backup = f"{self.filename}.{i + 1}"
                if os.path.exists(old_backup):
                    if os.path.exists(new_backup):
                        os.remove(new_backup)
                    os.rename(old_backup, new_backup)

            # Rotate current log file to .1
            first_backup = f"{self.filename}.1"
            if os.path.exists(first_backup):
                os.remove(first_backup)
            os.rename(self.filename, first_backup)
        except OSError:
            # Ignore rotation errors
            pass
