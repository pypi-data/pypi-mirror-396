"""
Test result handling utilities for test command.
"""

import sys


class TestResultHandler:
    """Handle test results and exit codes."""

    def handle_test_result(self, result, report_mode: bool) -> None:
        """
        Handle the test result based on return code.

        Args:
            result: The subprocess result object
            report_mode: Whether we're in report mode
        """
        if result.returncode == 0:
            # Tests passed
            if not report_mode:
                print("All tests passed successfully!")
        else:
            # Tests failed
            if not report_mode:
                # In quiet mode, show the output when tests fail
                if hasattr(result, "stdout") and result.stdout:
                    print(result.stdout)
                if hasattr(result, "stderr") and result.stderr:
                    print(result.stderr, file=sys.stderr)
                print(f"Tests failed with return code {result.returncode}")
            sys.exit(result.returncode)
