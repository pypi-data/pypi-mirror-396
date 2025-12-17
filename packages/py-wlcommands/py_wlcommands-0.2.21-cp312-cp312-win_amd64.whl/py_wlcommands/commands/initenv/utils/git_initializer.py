"""Git initializer utility."""

import os
import subprocess
from pathlib import Path

from ....utils.logging import log_info
from .exceptions import GitInitializationError
from .git.git_flow_manager import GitFlowManager
from .git.gitignore_manager import GitignoreManager
from .git.pre_commit_manager import PreCommitManager
from .log_manager import performance_monitor


class GitInitializer:
    """Git repository initializer."""

    def __init__(self, env: dict[str, str]) -> None:
        self.env = env
        self.gitignore_manager = GitignoreManager()
        self.pre_commit_manager = PreCommitManager()
        self.git_flow_manager = GitFlowManager(env)

    def _check_git_bash_installed(self) -> None:
        """
        Check if Git Bash is installed on Windows.

        Git Bash is required for Git hooks to work properly on Windows.
        If Git Bash is not found, display a warning message.
        If Git Bash is found but not in PATH, add its directory to the project environment.
        """
        try:
            # Try to find git bash in common locations
            common_paths = [
                r"C:\Program Files\Git\bin\bash.exe",
                r"C:\Program Files (x86)\Git\bin\bash.exe",
                r"C:\Git\bin\bash.exe",
            ]

            # Also check PATH environment variable
            path_env = os.environ.get("PATH", "")

            git_bash_path = None

            # Check common paths
            for path in common_paths:
                if Path(path).exists():
                    git_bash_path = path
                    break

            # If not found, check PATH
            if not git_bash_path:
                for path_dir in path_env.split(os.pathsep):
                    bash_path = Path(path_dir) / "bash.exe"
                    if bash_path.exists():
                        git_bash_path = str(bash_path)
                        break

            # If Git Bash is found
            if git_bash_path:
                git_bash_dir = str(Path(git_bash_path).parent)

                # Check if Git Bash directory is already in PATH
                if git_bash_dir not in path_env:
                    log_info(f"✓ Git Bash found at: {git_bash_path}")
                    log_info(f"✓ Git Bash 位于: {git_bash_path}", lang="zh")

                    # Add Git Bash directory to project environment
                    # This ensures hooks can find Git Bash during execution
                    os.environ["PATH"] = f"{git_bash_dir}{os.pathsep}{path_env}"
                    log_info(f"✓ Added Git Bash directory to PATH: {git_bash_dir}")
                    log_info(f"✓ 将Git Bash目录添加到PATH: {git_bash_dir}", lang="zh")
                else:
                    log_info(f"✓ Git Bash already in PATH: {git_bash_path}")
                    log_info(f"✓ Git Bash 已在PATH中: {git_bash_path}", lang="zh")

            # If still not found, display warning
            if not git_bash_path:
                log_info("Warning: Git Bash not found on Windows.")
                log_info("警告: 在Windows上未找到Git Bash。")
                log_info(
                    "Git Bash is required for Git hooks to work properly on Windows."
                )
                log_info("在Windows上，Git钩子需要Git Bash才能正常工作。")
                log_info(
                    "Please download and install Git Bash from: https://git-scm.com/"
                )
                log_info("请从以下地址下载并安装Git Bash: https://git-scm.com/")
                log_info(
                    "After installation, please restart your terminal and try again."
                )
                log_info("安装完成后，请重启终端并再次尝试。")
        except Exception as e:
            log_info(f"Warning: Error checking for Git Bash: {e}")
            log_info(f"警告: 检查Git Bash时出错: {e}")

    @performance_monitor
    def initialize(self) -> None:
        """
        Initialize Git repository if it doesn't exist.
        """
        # Check for Git Bash on Windows
        if os.name == "nt":
            self._check_git_bash_installed()

        # Copy .gitignore template if it doesn't exist and we're not in a test environment
        if not Path(".gitignore").exists() and not os.environ.get(
            "PYTEST_CURRENT_TEST"
        ):
            self.gitignore_manager.copy_gitignore_template()

        if not Path(".git").exists():
            log_info("Initializing Git repository...")
            log_info("初始化Git仓库...", lang="zh")
            try:
                subprocess.run(
                    ["git", "init"], check=True, capture_output=False, env=self.env
                )
                log_info("✓ Git repository initialized")
                log_info("✓ Git仓库初始化完成", lang="zh")
            except subprocess.CalledProcessError as e:
                log_info("Warning: Failed to initialize Git repository")
                log_info("警告: 初始化Git仓库失败", lang="zh")
                raise GitInitializationError(
                    f"Failed to initialize Git repository: {e}"
                )
        else:
            log_info("Git repository already exists, skipping initialization")
            log_info("Git仓库已存在，跳过初始化", lang="zh")

            # Update repository if it already exists (skip during tests)
            if not os.environ.get("PYTEST_CURRENT_TEST"):
                self.update_repository()

        # Setup Git Flow branches (main, develop, features) and switch to features
        if not os.environ.get("PYTEST_CURRENT_TEST"):
            self.git_flow_manager.setup_git_flow_branches()

    def setup_git_flow_branches(self, work_type: str) -> None:
        """Setup Git Flow branches based on work type."""
        self.git_flow_manager.setup_git_flow_branches_by_work_type(work_type)

    def update_repository(self) -> None:
        """Update the repository by pulling latest changes from all important branches."""
        log_info("Updating repository...")
        log_info("更新仓库...", lang="zh")

        # 拉取最新的main分支
        try:
            log_info("Pulling latest changes from main branch...")
            log_info("拉取main分支最新变更...", lang="zh")
            subprocess.run(
                ["git", "fetch", "origin", "main"],
                check=True,
                capture_output=False,
                env=self.env,
            )
            subprocess.run(
                ["git", "checkout", "main"],
                check=True,
                capture_output=False,
                env=self.env,
            )
            subprocess.run(
                ["git", "pull", "origin", "main"],
                check=True,
                capture_output=False,
                env=self.env,
            )
            log_info("✓ main branch updated")
            log_info("✓ main分支更新完成", lang="zh")
        except subprocess.CalledProcessError as e:
            log_info(f"Warning: Failed to update main branch: {e}")
            log_info(f"警告: 更新main分支失败: {e}", lang="zh")

        # 拉取最新的develop分支
        try:
            log_info("Pulling latest changes from develop branch...")
            log_info("拉取develop分支最新变更...", lang="zh")
            subprocess.run(
                ["git", "fetch", "origin", "develop"],
                check=True,
                capture_output=False,
                env=self.env,
            )
            subprocess.run(
                ["git", "checkout", "develop"],
                check=True,
                capture_output=False,
                env=self.env,
            )
            subprocess.run(
                ["git", "pull", "origin", "develop"],
                check=True,
                capture_output=False,
                env=self.env,
            )
            log_info("✓ develop branch updated")
            log_info("✓ develop分支更新完成", lang="zh")
        except subprocess.CalledProcessError as e:
            log_info(f"Warning: Failed to update develop branch: {e}")
            log_info(f"警告: 更新develop分支失败: {e}", lang="zh")

        # 拉取所有feature分支
        try:
            log_info("Pulling latest changes from all feature branches...")
            log_info("拉取所有feature分支最新变更...", lang="zh")
            # 获取所有远程feature分支
            result = subprocess.run(
                ["git", "branch", "-r"],
                check=True,
                capture_output=True,
                env=self.env,
                text=True,
            )
            feature_branches = [
                line.strip()
                for line in result.stdout.split("\n")
                if line.strip().startswith("origin/feature/")
            ]

            for branch in feature_branches:
                branch_name = branch.replace("origin/", "")
                log_info(f"Pulling {branch_name}...")
                log_info(f"拉取{branch_name}...", lang="zh")
                subprocess.run(
                    ["git", "fetch", "origin", branch_name],
                    check=True,
                    capture_output=False,
                    env=self.env,
                )

            log_info("✓ All feature branches updated")
            log_info("✓ 所有feature分支更新完成", lang="zh")
        except subprocess.CalledProcessError as e:
            log_info(f"Warning: Failed to update feature branches: {e}")
            log_info(f"警告: 更新feature分支失败: {e}", lang="zh")
