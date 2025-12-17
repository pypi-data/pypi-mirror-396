"""
Self update command.
"""

import shutil
import subprocess
import sys

from . import Command, register_command, validate_command_args

# Import the SelfCommand from the new modular package
from .selfcommands.self_command import SelfCommand

# Re-export for backward compatibility
__all__ = ["SelfCommand", "sys", "shutil", "subprocess"]

# For backward compatibility with tests that mock these modules
# We need to expose these modules as attributes in this module
# so that the mocks work correctly
import shutil as shutil
import subprocess as subprocess
import sys as sys
