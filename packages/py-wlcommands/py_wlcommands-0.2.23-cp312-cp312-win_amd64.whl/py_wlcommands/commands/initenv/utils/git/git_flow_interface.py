"""Git Flow 接口定义"""

from abc import ABC, abstractmethod


class GitFlowInterface(ABC):
    """Git Flow 接口，定义 Git Flow 操作的基本方法"""

    @abstractmethod
    def setup_git_flow_branches(self) -> None:
        """
        设置 Git Flow 分支结构
        """
        pass

    @abstractmethod
    def setup_git_flow_branches_by_work_type(self, work_type: str) -> None:
        """
        根据工作类型设置 Git Flow 分支

        Args:
            work_type: 工作类型 (feature, fix, hotfix, release)
        """
        pass
