"""Git LFS manager utility."""

import shutil
import subprocess
from pathlib import Path

from py_wlcommands.utils.logging import log_error, log_info, log_warning


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

    def _check_nested_git(self, auto_fix: bool = False) -> bool:
        """检查项目中是否存在嵌套的.git目录，并可选择自动修复

        Args:
            auto_fix: 是否自动移除嵌套的.git目录

        Returns:
            True if no nested .git directories are found or all were successfully fixed,
            False otherwise.
        """
        # 获取当前目录
        current_dir = Path.cwd()
        nested_git_dirs = []

        # 查找所有嵌套的.git目录（不包括根目录的.git）
        for git_dir in current_dir.glob("**/.git"):
            # 跳过根目录的.git文件夹
            if git_dir.parent == current_dir:
                continue

            # 检查是否是目录
            if git_dir.is_dir():
                nested_git_dirs.append(git_dir)

        # 如果找到嵌套的.git目录，记录警告并可选择自动修复
        if nested_git_dirs:
            log_warning("发现嵌套的.git目录，这可能导致Git操作失败:")
            log_warning("发现嵌套的.git目录，这可能导致Git操作失败:", lang="zh")

            for git_dir in nested_git_dirs:
                log_warning(f"  - {git_dir}")
                log_warning(f"  - {git_dir}", lang="zh")

            # 自动修复逻辑
            if auto_fix:
                log_info("\n正在自动移除嵌套的.git目录...")
                log_info("\n正在自动移除嵌套的.git目录...", lang="zh")

                all_removed = True
                for git_dir in nested_git_dirs:
                    try:
                        shutil.rmtree(git_dir)
                        log_info(f"✓ 成功移除: {git_dir}")
                        log_info(f"✓ 成功移除: {git_dir}", lang="zh")
                    except Exception as e:
                        log_error(f"✗ 移除失败 {git_dir}: {e}")
                        log_error(f"✗ 移除失败 {git_dir}: {e}", lang="zh")
                        all_removed = False

                return all_removed
            else:
                log_warning("\n建议移除这些嵌套的.git目录以避免Git操作问题。")
                log_warning(
                    "\n建议移除这些嵌套的.git目录以避免Git操作问题。", lang="zh"
                )
                log_warning("使用 --fix 选项可以自动移除这些嵌套的.git目录。")
                log_warning(
                    "使用 --fix 选项可以自动移除这些嵌套的.git目录。", lang="zh"
                )
                return False

        return True

    def initialize(self, auto_fix: bool = False) -> None:
        """初始化Git LFS.

        Args:
            auto_fix: 是否自动移除嵌套的.git目录

        Raises:
            Exception: If Git LFS initialization fails.
        """
        # 检查是否存在嵌套的.git目录
        self._check_nested_git(auto_fix)

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
