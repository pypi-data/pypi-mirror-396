from ....utils.logging import log_info as log_info
from .exceptions import GitInitializationError as GitInitializationError
from .git.git_flow_manager import GitFlowManager as GitFlowManager
from .git.gitignore_manager import GitignoreManager as GitignoreManager
from .git.pre_commit_manager import PreCommitManager as PreCommitManager
from .log_manager import performance_monitor as performance_monitor
from _typeshed import Incomplete

class GitInitializer:
    env: Incomplete
    gitignore_manager: Incomplete
    pre_commit_manager: Incomplete
    git_flow_manager: Incomplete
    def __init__(self, env: dict[str, str]) -> None: ...
    @performance_monitor
    def initialize(self) -> None: ...
    def setup_git_flow_branches(self, work_type: str) -> None: ...
    def update_repository(self) -> None: ...
