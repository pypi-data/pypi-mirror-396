"""Git 工具类，封装基础的 Git 操作"""

import os
import subprocess
import time


class GitUtility:
    """提供基础的 Git 操作功能"""

    def __init__(self, env: dict[str, str]):
        """
        初始化 GitUtility 类

        Args:
            env: 执行 Git 命令时使用的环境变量
        """
        self.env = env
        self.max_retries = 3
        self.retry_delay = 1.0  # 秒

    def _run_git_command(self, command, check=False, capture_output=False, text=True):
        """
        执行 Git 命令并处理 index.lock 错误，包含重试机制

        Args:
            command: 要执行的 Git 命令
            check: 是否检查返回码
            capture_output: 是否捕获输出
            text: 是否返回文本输出

        Returns:
            subprocess.CompletedProcess: 命令执行结果
        """
        for attempt in range(self.max_retries):
            try:
                return subprocess.run(
                    command,
                    check=check,
                    capture_output=capture_output,
                    text=text,
                    env=self.env,
                )
            except subprocess.CalledProcessError as e:
                # 检查是否是 index.lock 错误
                if b"index.lock" in (e.stdout + e.stderr) or "index.lock" in str(e):
                    if attempt < self.max_retries - 1:
                        # 等待一段时间后重试
                        time.sleep(self.retry_delay)
                        continue
                raise
            except Exception as e:
                # 检查是否是 index.lock 相关的文件操作错误
                if "index.lock" in str(e):
                    if attempt < self.max_retries - 1:
                        # 等待一段时间后重试
                        time.sleep(self.retry_delay)
                        continue
                raise
        # 如果所有重试都失败，再次执行命令让它抛出原始错误
        return subprocess.run(
            command,
            check=check,
            capture_output=capture_output,
            text=text,
            env=self.env,
        )

    def is_git_repository(self) -> bool:
        """
        检查当前目录是否在 Git 仓库内

        Returns:
            bool: 如果在 Git 仓库内返回 True，否则返回 False
        """
        result = self._run_git_command(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    def get_current_branch(self) -> str:
        """
        获取当前分支名称

        Returns:
            str: 当前分支名称
        """
        result = self._run_git_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()

    def branch_exists(self, branch_name: str) -> bool:
        """
        检查指定分支是否存在

        Args:
            branch_name: 要检查的分支名称

        Returns:
            bool: 如果分支存在返回 True，否则返回 False
        """
        result = self._run_git_command(
            ["git", "branch", "--list", branch_name],
            capture_output=True,
            text=True,
            check=False,
        )
        return branch_name in result.stdout

    def stage_all_files(self) -> None:
        """将所有文件添加到暂存区"""
        self._run_git_command(
            ["git", "add", "."],
            check=False,
            capture_output=False,
        )

    def commit_files(self, message: str) -> None:
        """
        提交暂存区的文件

        Args:
            message: 提交信息
        """
        self._run_git_command(
            ["git", "commit", "-m", message],
            check=False,
            capture_output=False,
        )

    def rename_branch(self, old_name: str, new_name: str) -> None:
        """
        重命名分支

        Args:
            old_name: 旧分支名称
            new_name: 新分支名称
        """
        self._run_git_command(
            ["git", "branch", "-M", new_name],
            check=False,
            capture_output=False,
        )

    def checkout_branch(self, branch_name: str) -> None:
        """
        切换到指定分支

        Args:
            branch_name: 要切换到的分支名称
        """
        self._run_git_command(
            ["git", "checkout", branch_name],
            check=False,
            capture_output=False,
        )

    def create_and_checkout_branch(
        self, branch_name: str, source_branch: str | None = None
    ) -> None:
        """
        创建并切换到新分支

        Args:
            branch_name: 新分支名称
            source_branch: 源分支名称（可选）
        """
        if source_branch:
            self._run_git_command(
                ["git", "checkout", "-b", branch_name, source_branch],
                check=False,
                capture_output=False,
            )
        else:
            self._run_git_command(
                ["git", "checkout", "-b", branch_name],
                check=False,
                capture_output=False,
            )

    def pull_branch(self, branch_name: str, remote: str = "origin") -> None:
        """
        拉取指定分支的最新更改

        Args:
            branch_name: 分支名称
            remote: 远程仓库名称（默认: origin）
        """
        self._run_git_command(
            ["git", "pull", remote, branch_name],
            check=True,
            capture_output=False,
        )

    def create_branch_from_remote(
        self, branch_name: str, remote: str = "origin"
    ) -> None:
        """
        从远程创建本地分支

        Args:
            branch_name: 分支名称
            remote: 远程仓库名称（默认: origin）
        """
        self._run_git_command(
            ["git", "checkout", "-b", branch_name, f"{remote}/{branch_name}"],
            check=True,
            capture_output=False,
        )

    def local_branch_exists(self, branch_name: str) -> bool:
        """
        检查本地分支是否存在

        Args:
            branch_name: 分支名称

        Returns:
            bool: 如果本地分支存在返回 True，否则返回 False
        """
        result = self._run_git_command(
            ["git", "branch", "--list", branch_name],
            check=False,
            capture_output=True,
            text=True,
        )
        return branch_name in result.stdout
