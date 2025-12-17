"""分支创建器，处理 Git Flow 分支创建逻辑"""

import subprocess

from py_wlcommands.utils.logging import log_info


class BranchCreator:
    """处理 Git Flow 分支创建逻辑"""

    def __init__(self, git_utility):
        """
        初始化 BranchCreator 类

        Args:
            git_utility: GitUtility 实例，用于执行基础 Git 操作
        """
        self.git_utility = git_utility

    def setup_initial_branches(self) -> None:
        """设置初始的 Git Flow 分支结构（main 和 develop）"""
        import time

        log_info("Starting setup_initial_branches...")
        log_info("开始设置初始分支...", lang="zh")

        current_branch = self.git_utility.get_current_branch()
        log_info(f"Current branch: {current_branch}")
        log_info(f"当前分支: {current_branch}", lang="zh")

        # 检查并创建 main 分支
        if not self.git_utility.branch_exists("main"):
            log_info("Creating main branch...")
            log_info("创建 main 分支...", lang="zh")

            # 直接创建 main 分支，不依赖提交
            if current_branch != "main":
                log_info("Creating main branch directly...")
                self.git_utility.create_and_checkout_branch("main")
                # 等待一段时间，确保 Git 有足够时间释放锁
                time.sleep(0.5)
            else:
                log_info("Already on main branch")

            log_info("✓ Main branch created")
            log_info("✓ Main 分支创建成功", lang="zh")
        else:
            log_info("Main branch already exists")
            log_info("Main 分支已存在", lang="zh")
            # 确保我们在 main 分支上
            self.git_utility.checkout_branch("main")
            # 等待一段时间，确保 Git 有足够时间释放锁
            time.sleep(0.5)

        # 检查并创建 develop 分支
        if not self.git_utility.branch_exists("develop"):
            log_info("Creating develop branch...")
            log_info("创建 develop 分支...", lang="zh")

            # 直接创建 develop 分支，不依赖 main 分支的提交
            log_info("Creating develop branch directly...")
            self.git_utility.create_and_checkout_branch("develop")
            # 等待一段时间，确保 Git 有足够时间释放锁
            time.sleep(0.5)

            log_info("✓ Develop branch created")
            log_info("✓ Develop 分支创建成功", lang="zh")
        else:
            log_info("Develop branch already exists")
            log_info("Develop 分支已存在", lang="zh")
            # 确保我们在 develop 分支上
            self.git_utility.checkout_branch("develop")
            # 等待一段时间，确保 Git 有足够时间释放锁
            time.sleep(0.5)

    def check_and_pull_branch(self, branch_name: str) -> None:
        """
        检查分支是否存在并拉取最新更改

        Args:
            branch_name: 要检查和拉取的分支名称
        """
        log_info(f"Checking and pulling {branch_name} branch...")
        log_info(f"正在检查并拉取 {branch_name} 分支...", lang="zh")

        try:
            # Check if branch exists locally
            if self.git_utility.local_branch_exists(branch_name):
                # Branch exists locally, check if it's tracking remote
                self.git_utility.checkout_branch(branch_name)

                # Pull latest changes
                self.git_utility.pull_branch(branch_name)
                log_info(f"✓ {branch_name} branch pulled successfully")
                log_info(f"✓ {branch_name} 分支拉取成功", lang="zh")
            else:
                # Branch doesn't exist locally, checkout from remote
                self.git_utility.create_branch_from_remote(branch_name)
                log_info(f"✓ {branch_name} branch created from remote")
                log_info(f"✓ 从远程创建 {branch_name} 分支成功", lang="zh")
        except subprocess.CalledProcessError as e:
            log_info(f"Warning: Failed to check and pull {branch_name} branch")
            log_info(f"警告: 检查并拉取 {branch_name} 分支失败", lang="zh")
            log_info(f"Error details: {e}")
            log_info(f"错误详情: {e}", lang="zh")

    def create_git_flow_branch(self, work_type: str, source_branch: str) -> None:
        """
        根据工作类型创建 Git Flow 分支

        Args:
            work_type: 工作类型 (feature, fix, hotfix, release)
            source_branch: 源分支名称
        """
        log_info(f"Creating {work_type} branch from {source_branch}...")
        log_info(f"正在从 {source_branch} 创建 {work_type} 分支...", lang="zh")

        try:
            # Get current branch name
            current_branch = self.git_utility.get_current_branch()

            # Checkout source branch if not already on it
            if current_branch != source_branch:
                self.git_utility.checkout_branch(source_branch)

            # Get user input for branch name
            branch_name = input(
                f"Enter {work_type} branch name (e.g., {work_type}/my-feature): "
            )

            # Validate branch name
            if not branch_name.startswith(f"{work_type}/"):
                branch_name = f"{work_type}/{branch_name}"

            # Create and checkout new branch
            self.git_utility.create_and_checkout_branch(branch_name)

            log_info(f"✓ Created and checked out {branch_name} branch")
            log_info(f"✓ 创建并切换到 {branch_name} 分支成功", lang="zh")
        except subprocess.CalledProcessError as e:
            log_info(f"Warning: Failed to create {work_type} branch")
            log_info(f"警告: 创建 {work_type} 分支失败", lang="zh")
            log_info(f"Error details: {e}")
            log_info(f"错误详情: {e}", lang="zh")
        except KeyboardInterrupt:
            log_info("\nOperation cancelled by user")
            log_info("\n用户取消了操作", lang="zh")
