"""
Structured logging implementation for WL Commands.
"""

# Import the modularized StructuredLogger from the structured_logging package
# This maintains backward compatibility while allowing for modular code organization
import datetime

# Import and re-export module-level attributes used by tests
from .log_rotators import LogRotator
from .structured_logging import StructuredLogger

# Re-export for backward compatibility
__all__ = ["StructuredLogger"]
