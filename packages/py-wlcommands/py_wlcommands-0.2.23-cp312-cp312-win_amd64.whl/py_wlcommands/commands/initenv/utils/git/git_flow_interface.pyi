import abc
from abc import ABC, abstractmethod

class GitFlowInterface(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def setup_git_flow_branches(self) -> None: ...
    @abstractmethod
    def setup_git_flow_branches_by_work_type(self, work_type: str) -> None: ...
