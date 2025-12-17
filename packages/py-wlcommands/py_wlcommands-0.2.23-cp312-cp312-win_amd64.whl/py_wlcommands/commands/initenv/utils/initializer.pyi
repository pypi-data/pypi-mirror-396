from ....utils.logging import log_info as log_info
from ....utils.workspace_detector import WorkspaceDetector as WorkspaceDetector
from .cargo_sync import sync_toml_files as sync_toml_files
from .config_manager import ConfigManager as ConfigManager
from .i18n_manager import I18nManager as I18nManager
from .log_manager import LogManager as LogManager
from .project_structure import ProjectStructureSetup as ProjectStructureSetup
from .pyproject_generator import PyProjectGenerator as PyProjectGenerator
from .rust_initializer import RustInitializer as RustInitializer
from .venv_manager import VenvManager as VenvManager
from _typeshed import Incomplete

class Initializer:
    env: Incomplete
    project_name: Incomplete
    config_manager: Incomplete
    i18n_manager: Incomplete
    log_manager: Incomplete
    workspace_detector: Incomplete
    project_structure_setup: Incomplete
    rust_initializer: Incomplete
    venv_manager: Incomplete
    def __init__(self, env: dict[str, str]) -> None: ...
    def check_uv_installed(self) -> None: ...
    def setup_project_structure(self) -> None: ...
    def init_rust(self) -> None: ...
    def generate_pyproject(self) -> None: ...
    def sync_cargo_toml(self) -> None: ...
    def create_venv(self, is_windows: bool) -> None: ...
    def is_project_initialized(self) -> bool: ...
    def update_project(self) -> None: ...
