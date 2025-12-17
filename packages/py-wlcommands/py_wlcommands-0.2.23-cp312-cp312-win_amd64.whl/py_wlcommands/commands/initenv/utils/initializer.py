"""Project initializer coordinator."""

import subprocess
from pathlib import Path

from ....utils.logging import log_info
from ....utils.workspace_detector import WorkspaceDetector
from .cargo_sync import sync_toml_files
from .config_manager import ConfigManager
from .i18n_manager import I18nManager
from .log_manager import LogManager
from .project_structure import ProjectStructureSetup
from .pyproject_generator import PyProjectGenerator
from .rust_initializer import RustInitializer
from .venv_manager import VenvManager


class Initializer:
    """Coordinator for project initialization."""

    def __init__(self, env: dict[str, str]) -> None:
        self.env = env
        self.project_name = Path.cwd().name
        self.config_manager = ConfigManager()
        self.i18n_manager = I18nManager()
        self.log_manager = LogManager()
        self.workspace_detector = WorkspaceDetector()

        # Initialize sub-components
        self.project_structure_setup = ProjectStructureSetup()
        self.rust_initializer = RustInitializer()
        self.venv_manager = VenvManager(env)

    def check_uv_installed(self) -> None:
        """Check if uv is installed."""
        try:
            subprocess.run(
                ["uv", "--version"], check=True, capture_output=True, env=self.env
            )
            log_info("✓ uv command found.")
            log_info("✓ 找到 uv 命令。", lang="zh")
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            from ....exceptions import CommandError

            raise CommandError(
                "uv command not found. Please install uv first (e.g., pip install uv) and try again."
            )

    def setup_project_structure(self) -> None:
        """Setup project structure."""
        log_info("Setting up project structure...")
        log_info("设置项目结构...", lang="zh")

        try:
            self.project_structure_setup.setup(self.project_name)
        except OSError as e:
            log_info(f"Warning: Failed to setup project structure: {e}")
            log_info(f"警告: 设置项目结构失败: {e}", lang="zh")

    def init_rust(self) -> None:
        """Initialize Rust environment."""
        log_info("Initializing Rust environment...")
        log_info("初始化Rust环境...", lang="zh")

        try:
            self.rust_initializer.initialize()
        except (OSError, subprocess.CalledProcessError) as e:
            log_info(f"Warning: Failed to initialize Rust environment: {e}")
            log_info(f"警告: 初始化Rust环境失败: {e}", lang="zh")

    def generate_pyproject(self) -> None:
        """Generate pyproject.toml if it doesn't exist."""
        if not Path("pyproject.toml").exists():
            log_info("pyproject.toml not found, generating...")
            log_info("未找到 pyproject.toml，正在生成...", lang="zh")

            try:
                # Create PyProjectGenerator instance and generate pyproject.toml
                generator = PyProjectGenerator(self.project_name)
                generator.set_project_info()
                generator.set_build_system(is_rust=Path("rust").exists())
                generator.set_development_tools()
                generator.generate()

                log_info("✓ pyproject.toml generated successfully")
                log_info("✓ pyproject.toml 生成成功", lang="zh")
            except (OSError, ValueError) as e:
                log_info(f"Warning: Failed to generate pyproject.toml: {e}")
                log_info(f"警告: 生成 pyproject.toml 失败: {e}", lang="zh")

    def sync_cargo_toml(self) -> None:
        """Sync Cargo.toml with pyproject.toml."""
        try:
            sync_toml_files(Path("pyproject.toml"), Path("rust/Cargo.toml"))
            log_info("✓ rust/Cargo.toml 已成功同步和更新。")
        except (OSError, ValueError) as e:
            log_info(f"Warning: Failed to sync Cargo.toml: {e}")
            log_info(f"警告: 同步 Cargo.toml 失败: {e}", lang="zh")

    def create_venv(self, is_windows: bool) -> None:
        """Create virtual environment."""
        if is_windows:
            self._create_venv_windows()
        else:
            self._create_venv_unix()

    def _detect_uv_workspace(self) -> bool:
        return self.workspace_detector.detect(Path.cwd())

    def _create_venv_windows(self) -> None:
        """Create virtual environment on Windows."""
        # Check uv workspace status and create venv if needed
        log_info(
            "Checking uv workspace status to determine if virtual environment should be created..."
        )
        log_info("检查uv workspace状态以决定是否创建虚拟环境...", lang="zh")

        if self._detect_uv_workspace():
            log_info(
                "✓ uv workspace environment detected, skipping local .venv creation"
            )
            log_info("✓ 检测到uv workspace环境，跳过创建本地.venv", lang="zh")
        else:
            log_info("Ensuring virtual environment exists...")
            log_info("确保虚拟环境存在...", lang="zh")
            # Create virtual environment directly instead of calling external script
            venv_path = self.config_manager.get("venv_path", ".venv")
            python_version = self.config_manager.get("python_version", "3.10")
            if not self.venv_manager.create_venv_windows(venv_path, python_version):
                log_info("Warning: Failed to create virtual environment")
                log_info("警告: 创建虚拟环境失败", lang="zh")

    def _create_venv_unix(self) -> None:
        """Create virtual environment on Unix-like systems."""
        log_info(
            "Checking uv workspace status to determine if virtual environment should be created..."
        )
        log_info("检查uv workspace状态以决定是否创建虚拟环境...", lang="zh")

        if self._detect_uv_workspace():
            log_info(
                "✓ uv workspace environment detected, skipping local .venv creation"
            )
            log_info("✓ 检测到uv workspace环境，跳过创建本地.venv", lang="zh")
        else:
            log_info("Ensuring virtual environment exists...")
            log_info("确保虚拟环境存在...", lang="zh")
            venv_path = self.config_manager.get("venv_path", ".venv")
            python_version = self.config_manager.get("python_version", "3.10")
            if not self.venv_manager.create_venv_unix(
                venv_path, python_version, self.env
            ):
                log_info("Warning: Failed to create virtual environment")
                log_info("警告: 创建虚拟环境失败", lang="zh")

    def is_project_initialized(self) -> bool:
        """Check if the project is already initialized."""
        # 检测项目是否已经初始化
        # 检查是否存在pyproject.toml文件
        is_pyproject_exists = Path("pyproject.toml").exists()

        return is_pyproject_exists

    def update_project(self) -> None:
        """Update the project by syncing environment."""
        # 确保项目结构（包括.wl目录）存在
        log_info("Ensuring project structure exists...")
        log_info("确保项目结构存在...", lang="zh")
        self.setup_project_structure()

        # 确保pyproject.toml是最新的
        self.generate_pyproject()

        # 同步Cargo.toml与pyproject.toml
        self.sync_cargo_toml()

        # 同步uv环境
        self.venv_manager.sync_environment()

        log_info("✓ Project update completed")
        log_info("✓ 项目更新完成", lang="zh")
