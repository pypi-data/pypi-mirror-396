"""项目结构初始化处理器"""

import shutil
import subprocess
from pathlib import Path

from py_wlcommands.commands.initenv.utils.platform_adapter import PlatformAdapter
from py_wlcommands.commands.initenv.utils.project_structure import ProjectStructureSetup
from py_wlcommands.utils.logging import log_error, log_info


class InitProjectHandler:
    """处理项目结构初始化的类"""

    @staticmethod
    def initialize() -> None:
        """
        初始化项目结构，包括apps和packages文件夹
        """
        # 检查pyproject.toml是否存在，避免覆盖现有项目
        if Path("pyproject.toml").exists():
            log_info("pyproject.toml already exists. Skipping project initialization.")
            log_info("pyproject.toml 已存在。跳过项目初始化。", lang="zh")
            return

        log_info("=== Starting initialization of project structure ===")
        log_info("=== 开始初始化项目结构 ===", lang="zh")

        # 创建apps和packages目录
        Path("apps").mkdir(exist_ok=True)
        Path("packages").mkdir(exist_ok=True)
        log_info("✓ Created apps and packages directories")
        log_info("✓ 创建 apps 和 packages 目录", lang="zh")

        # 获取供应商模板目录
        current_file = Path(__file__)
        vendor_project_dir = (
            current_file.parent / ".." / ".." / ".." / "vendors" / "project"
        )
        vendor_project_dir = vendor_project_dir.resolve()

        template_files = [
            ".gitignore",
            ".python-version",
            "README.md",
            "pyproject.toml",
        ]

        for file_name in template_files:
            source_file = vendor_project_dir / file_name
            target_file = Path(file_name)

            if source_file.exists():
                shutil.copy2(source_file, target_file)
            else:
                log_error(f"Template file {file_name} not found")
                log_error(f"未找到模板文件 {file_name}", lang="zh")

        # 设置项目结构，包括.wl目录和配置文件
        project_structure = ProjectStructureSetup()
        project_name = Path.cwd().name
        project_structure.setup(project_name)

        # 使用'uv run'初始化uv环境
        env = PlatformAdapter.get_env()
        try:
            result = subprocess.run(
                ["uv", "run", "python", "--version"],
                capture_output=True,
                env=env,
                text=True,
                encoding="utf-8",
            )
            if result.returncode == 0:
                log_info("✓ UV environment initialized")
                log_info("✓ UV 环境已初始化", lang="zh")
            else:
                log_info(
                    f"Warning: UV environment initialization warning: {result.stderr}"
                )
                log_info(f"警告: UV 环境初始化警告: {result.stderr}", lang="zh")
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
            log_info(f"Warning: Failed to initialize UV environment: {e}")
            log_info(f"警告: 初始化 UV 环境失败: {e}", lang="zh")

        log_info("Project structure initialization completed!")
