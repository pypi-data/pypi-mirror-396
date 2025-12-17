#!/usr/bin/env python3

"""
Main entry point for WL Commands.
"""


def main() -> None:
    # Use a try/except block to support both direct execution and module execution
    try:
        # Local import to avoid import issues
        from .cli import main as cli_main
    except ImportError:
        # Fallback for cases where relative imports don't work
        from py_wlcommands.cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
