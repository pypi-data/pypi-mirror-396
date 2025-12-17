import argparse
from .. import Command as Command, register_command as register_command, validate_command_args as validate_command_args
from ..self import shutil as shutil, subprocess as subprocess, sys as sys
from .installation_manager import InstallationManager as InstallationManager
from .local_installer import LocalInstaller as LocalInstaller
from .pypi_updater import PypiUpdater as PypiUpdater
from .windows_update import WindowsUpdate as WindowsUpdate

class SelfCommand(Command):
    @property
    def name(self) -> str: ...
    @property
    def help(self) -> str: ...
    def add_arguments(self, parser: argparse.ArgumentParser) -> None: ...
    def execute(self, subcommand: str = 'update', path: str = None) -> None: ...
