"""Git Flow 分支管理器"""

import os
import time

from py_wlcommands.utils.logging import log_info

from .branch_creator import BranchCreator
from .git_flow_interface import GitFlowInterface

# 导入新创建的模块
from .git_utility import GitUtility


class GitFlowManager(GitFlowInterface):
    """Git Flow 分支管理器，实现 Git Flow 接口"""

    def __init__(self, env: dict[str, str]) -> None:
        """
        初始化 GitFlowManager 类

        Args:
            env: 执行 Git 命令时使用的环境变量
        """
        self.env = env
        self.git_utility = GitUtility(env)
        self.branch_creator = BranchCreator(self.git_utility)

    def _cleanup_index_lock(self) -> None:
        """
        检查并清理可能存在的 index.lock 文件
        在 Windows 上，Git 操作可能会留下未及时删除的 index.lock 文件
        """
        # 检查 .git/index.lock 文件是否存在
        index_lock_path = os.path.join(".git", "index.lock")
        if os.path.exists(index_lock_path):
            try:
                # 尝试删除 index.lock 文件
                os.remove(index_lock_path)
                log_info("✓ Cleaned up existing index.lock file")
                log_info("✓ 清理了存在的 index.lock 文件", lang="zh")
                # 等待一小段时间，确保文件系统完成删除操作
                time.sleep(0.3)
            except OSError as e:
                log_info(f"Warning: Failed to remove index.lock file: {e}")
                log_info(f"警告: 无法删除 index.lock 文件: {e}", lang="zh")

    def setup_git_flow_branches(self) -> None:
        """
        设置 Git Flow 分支结构

        创建主开发分支 (main)、开发分支 (develop)、功能分支 (features)，
        并确保所有分支都拉取最新代码。如果分支已存在，则直接切换到该分支。
        """
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return

        log_info("Setting up Git Flow branches...")
        log_info("设置 Git Flow 分支结构...", lang="zh")

        try:
            # 检查并清理可能存在的 index.lock 文件
            self._cleanup_index_lock()

            # Check if we're in a git repository
            if not self.git_utility.is_git_repository():
                log_info("Warning: Not inside a git repository")
                log_info("警告: 不在 git 仓库内", lang="zh")
                return

            # 设置初始分支（main 和 develop）
            self.branch_creator.setup_initial_branches()

            # 检查并清理可能存在的 index.lock 文件
            self._cleanup_index_lock()

            # 检查并创建 features 分支（默认快速开发分支）
            log_info("Creating features branch...")
            log_info("创建 features 分支...", lang="zh")

            if not self.git_utility.branch_exists("features"):
                # 直接创建 features 分支，不依赖 develop 分支的提交
                self.git_utility.create_and_checkout_branch("features")
                log_info("✓ features branch created")
                log_info("✓ features 分支创建成功", lang="zh")
            else:
                log_info("features branch already exists")
                log_info("features 分支已存在", lang="zh")
                # 确保我们在 features 分支上
                self.git_utility.checkout_branch("features")

            log_info("Git Flow branches setup completed")
            log_info("Git Flow 分支设置完成", lang="zh")
        except Exception as e:
            log_info(f"Warning: Failed to set up Git Flow branches: {e}")
            log_info(f"警告: 设置 Git Flow 分支失败: {e}", lang="zh")

    def setup_git_flow_branches_by_work_type(self, work_type: str) -> None:
        """
        根据工作类型设置 Git Flow 分支

        Args:
            work_type: 工作类型 (feature, fix, hotfix, release)
        """
        # Define branch sources based on work type
        branch_sources = {
            "feature": "develop",
            "features": "develop",
            "fix": "develop",
            "hotfix": "main",
            "release": "develop",
        }

        # Get the source branch for the current work type
        source_branch = branch_sources[work_type]

        # Check and pull main branch
        if work_type in ["feature", "fix", "release"]:
            self.branch_creator.check_and_pull_branch("main")

        # Check and pull develop branch
        if work_type in ["feature", "fix", "release"]:
            self.branch_creator.check_and_pull_branch("develop")

        # Check and pull source branch (if it's different from main/develop) or for hotfix
        if source_branch not in ["main", "develop"] or work_type == "hotfix":
            self.branch_creator.check_and_pull_branch(source_branch)

        # Create the new branch based on work type
        self.branch_creator.create_git_flow_branch(work_type, source_branch)
