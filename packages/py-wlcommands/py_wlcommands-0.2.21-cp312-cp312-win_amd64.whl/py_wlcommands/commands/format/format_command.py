"""
Format code command - legacy file for backward compatibility.
"""

# This file is kept for backward compatibility
# All format functionality has been moved to separate modules under the format package

from .format_coordinator import FormatCoordinator

# Keep the original class name for backward compatibility
FormatCommand = FormatCoordinator
