"""Platform adapter utility."""

import os
import platform
import sys


class PlatformAdapter:
    """Platform adapter for Windows and Unix-like systems."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_system() -> str:
        """Get the current system name."""
        return platform.system().lower()

    @staticmethod
    def is_windows() -> bool:
        """Check if the current system is Windows."""
        return PlatformAdapter.get_system() == "windows"

    @staticmethod
    def get_env() -> dict[str, str]:
        """Get environment variables for the current platform."""
        env = os.environ.copy()

        if PlatformAdapter.is_windows():
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONLEGACYWINDOWSFSENCODING"] = "1"
        else:
            env["PYTHONIOENCODING"] = "utf-8"

        return env

    @staticmethod
    def get_encoding() -> str:
        """Get the appropriate encoding for the current platform."""
        if PlatformAdapter.is_windows():
            return "utf-8" if sys.platform.startswith("win") else ""
        return "utf-8"
