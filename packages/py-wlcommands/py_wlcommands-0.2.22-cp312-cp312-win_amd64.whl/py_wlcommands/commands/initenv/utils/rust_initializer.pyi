from ....utils.logging import log_info as log_info
from .exceptions import RustInitializationError as RustInitializationError
from .log_manager import performance_monitor as performance_monitor
from .pyproject_generator import clean_cargo_name as clean_cargo_name

class RustInitializer:
    def __init__(self) -> None: ...
    @performance_monitor
    def initialize(self) -> None: ...
