"""Project structure setup utility."""

# Import all functionality from the modularized package
from .project_structure import (
    ProjectStructureSetup,
    _copy_and_configure_hooks,
    _create_init_files,
    _create_readme,
    _create_required_directories,
    setup_project_structure,
)

__all__ = [
    "ProjectStructureSetup",
    "setup_project_structure",
    "_copy_and_configure_hooks",
    "_create_required_directories",
    "_create_init_files",
    "_create_readme",
]
