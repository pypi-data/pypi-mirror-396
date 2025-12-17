"""Git LFS manager utility."""

import subprocess
from pathlib import Path

from py_wlcommands.utils.logging import log_error, log_info


class GitLFSManager:
    """Git LFS manager for initializing and configuring Git LFS."""

    def __init__(self, env: dict[str, str]) -> None:
        """Initialize Git LFS manager.

        Args:
            env: Environment variables for subprocess calls.
        """
        self.env = env
        # 常见的3D模型文件类型
        self.three_d_file_types = [
            # SolidWorks
            "*.sldprt",
            "*.sldasm",
            "*.slddrw",
            # CAD
            "*.dwg",
            "*.dxf",
            # 3D交换格式
            "*.iges",
            "*.igs",
            "*.step",
            "*.stp",
            # 3D打印格式
            "*.stl",
            # 其他常见的3D模型格式
            "*.obj",
            "*.fbx",
            "*.blend",
            "*.3ds",
        ]

    def _check_git_lfs_installed(self) -> bool:
        """检查Git LFS是否已安装.

        Returns:
            True if Git LFS is installed, False otherwise.
        """
        try:
            result = subprocess.run(
                ["git", "lfs", "version"],
                check=True,
                capture_output=True,
                env=self.env,
                text=True,
            )
            log_info(f"✓ Git LFS is installed: {result.stdout.strip()}")
            log_info(f"✓ Git LFS 已安装: {result.stdout.strip()}", lang="zh")
            return True
        except subprocess.CalledProcessError:
            log_error("✗ Git LFS is not installed")
            log_error("✗ Git LFS 未安装", lang="zh")
            log_error("Please install Git LFS from https://git-lfs.com/")
            log_error("请从 https://git-lfs.com/ 安装 Git LFS", lang="zh")
            return False
        except FileNotFoundError:
            log_error("✗ Git is not installed")
            log_error("✗ Git 未安装", lang="zh")
            return False

    def _install_git_lfs(self) -> bool:
        """安装Git LFS.

        Returns:
            True if Git LFS is installed successfully, False otherwise.
        """
        try:
            log_info("Initializing Git LFS...")
            log_info("初始化 Git LFS...", lang="zh")
            subprocess.run(
                ["git", "lfs", "install", "--force"],
                check=True,
                capture_output=False,
                env=self.env,
            )
            log_info("✓ Git LFS initialized")
            log_info("✓ Git LFS 初始化完成", lang="zh")
            return True
        except subprocess.CalledProcessError as e:
            log_error(f"✗ Failed to initialize Git LFS: {e}")
            log_error(f"✗ 初始化 Git LFS 失败: {e}", lang="zh")
            return False

    def _configure_lfs_tracking(self) -> None:
        """配置Git LFS跟踪3D模型文件类型."""
        log_info("Configuring Git LFS to track 3D model files...")
        log_info("配置 Git LFS 跟踪3D模型文件...", lang="zh")

        # 跟踪所有3D模型文件类型
        for file_type in self.three_d_file_types:
            try:
                subprocess.run(
                    ["git", "lfs", "track", file_type],
                    check=True,
                    capture_output=False,
                    env=self.env,
                )
                log_info(f"✓ Tracking {file_type}")
                log_info(f"✓ 跟踪 {file_type}", lang="zh")
            except subprocess.CalledProcessError as e:
                log_error(f"✗ Failed to track {file_type}: {e}")
                log_error(f"✗ 跟踪 {file_type} 失败: {e}", lang="zh")

        # 确保.gitattributes文件被添加到Git
        if Path(".gitattributes").exists():
            try:
                subprocess.run(
                    ["git", "add", ".gitattributes"],
                    check=True,
                    capture_output=False,
                    env=self.env,
                )
                log_info("✓ Added .gitattributes to Git")
                log_info("✓ 将 .gitattributes 添加到 Git", lang="zh")
            except subprocess.CalledProcessError as e:
                log_error(f"✗ Failed to add .gitattributes to Git: {e}")
                log_error(f"✗ 将 .gitattributes 添加到 Git 失败: {e}", lang="zh")

    def initialize(self) -> None:
        """初始化Git LFS.

        Raises:
            Exception: If Git LFS initialization fails.
        """
        # 检查Git LFS是否已安装
        if not self._check_git_lfs_installed():
            raise RuntimeError(
                "Git LFS is not installed. Please install Git LFS first."
            )

        # 安装Git LFS
        if not self._install_git_lfs():
            raise RuntimeError("Failed to initialize Git LFS.")

        # 配置Git LFS跟踪3D模型文件类型
        self._configure_lfs_tracking()

        log_info("\n✓ Git LFS initialization completed successfully!")
        log_info("✓ Git LFS 初始化成功完成！", lang="zh")
        log_info("\nGit LFS is now configured to track the following file types:")
        log_info("Git LFS 现已配置为跟踪以下文件类型：", lang="zh")
        for file_type in self.three_d_file_types:
            log_info(f"  - {file_type}")
            log_info(f"  - {file_type}", lang="zh")
        log_info(
            "\nYou can now use Git commands as usual to manage your 3D model files."
        )
        log_info("现在您可以像往常一样使用 Git 命令来管理您的 3D 模型文件。", lang="zh")
