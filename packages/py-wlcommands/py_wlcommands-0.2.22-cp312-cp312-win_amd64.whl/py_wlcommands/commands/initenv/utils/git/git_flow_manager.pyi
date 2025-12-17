from .branch_creator import BranchCreator as BranchCreator
from .git_flow_interface import GitFlowInterface as GitFlowInterface
from .git_utility import GitUtility as GitUtility
from _typeshed import Incomplete
from py_wlcommands.utils.logging import log_info as log_info

class GitFlowManager(GitFlowInterface):
    env: Incomplete
    git_utility: Incomplete
    branch_creator: Incomplete
    def __init__(self, env: dict[str, str]) -> None: ...
    def setup_git_flow_branches(self) -> None: ...
    def setup_git_flow_branches_by_work_type(self, work_type: str) -> None: ...
