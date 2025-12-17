"""
Lint command - legacy file for backward compatibility.
"""

# This file is kept for backward compatibility
# All lint functionality has been moved to separate modules under the lint package

from .lint_command import LintCommandImpl

# Keep the original class name for backward compatibility
LintCommand = LintCommandImpl
