from .....utils.logging import log_info as log_info
from .....utils.workspace_detector.venv_resolver import get_active_venv_path_str as get_active_venv_path_str
from ..config_manager import ConfigManager as ConfigManager
from ..log_manager import performance_monitor as performance_monitor
from _typeshed import Incomplete

class ProjectStructureSetup:
    config_manager: Incomplete
    def __init__(self) -> None: ...
    @performance_monitor
    def setup(self, project_name: str) -> None: ...
