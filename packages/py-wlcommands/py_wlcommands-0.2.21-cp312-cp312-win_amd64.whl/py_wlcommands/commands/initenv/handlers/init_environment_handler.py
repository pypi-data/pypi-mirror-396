"""环境初始化处理器"""

from py_wlcommands.commands.initenv.utils.initializer import Initializer
from py_wlcommands.commands.initenv.utils.platform_adapter import PlatformAdapter
from py_wlcommands.utils.logging import log_info


class InitEnvironmentHandler:
    """处理项目环境初始化的类"""

    @staticmethod
    def initialize(**kwargs) -> None:
        """
        初始化完整的项目环境

        Args:
            **kwargs: 命令行参数，包括日志配置参数
        """
        log_info("=== Starting initialization of project environment ===")
        log_info("=== 开始初始化项目环境 ===", lang="zh")

        # 检测平台
        is_windows = PlatformAdapter.is_windows()
        env = PlatformAdapter.get_env()

        # 创建初始化器
        initializer = Initializer(env)

        # 检查uv是否安装
        initializer.check_uv_installed()

        # 应用日志配置
        from py_wlcommands.utils.config import get_config_manager

        config_manager = get_config_manager()

        # 从kwargs中获取日志配置
        log_level = kwargs.get("log_level")
        log_console = kwargs.get("log_console")
        log_file = kwargs.get("log_file")

        # 更新配置
        if log_level:
            config_manager.set("log_level", log_level)
        if log_console is not None:
            config_manager.set("log_console", log_console)
        if log_file:
            config_manager.set("log_file", log_file)

        # 检测项目是否已经初始化
        is_initialized = initializer.is_project_initialized()

        if is_initialized:
            log_info("=== Project already initialized, performing daily update ===")
            log_info("=== 项目已初始化，执行每日更新 ===", lang="zh")
            # 执行更新流程
            initializer.update_project()
        else:
            # 执行完整初始化流程
            # 设置项目结构
            initializer.setup_project_structure()

            # 初始化Rust（如果需要）
            initializer.init_rust()

            # 生成pyproject.toml（如果需要）
            # 在init_rust之后执行，以便正确检测Rust环境
            initializer.generate_pyproject()

            # 同步Cargo.toml与pyproject.toml
            initializer.sync_cargo_toml()

            # 创建虚拟环境
            initializer.create_venv(is_windows)

        # 平台特定的最终化操作
        if is_windows:
            InitEnvironmentHandler._finalize_windows()
        else:
            InitEnvironmentHandler._finalize_unix()

        log_info("Project environment initialization completed!")
        log_info("项目环境初始化完成!", lang="zh")

    @staticmethod
    def _finalize_windows() -> None:
        """Windows平台的最终化操作"""
        log_info("✓ Windows-specific finalization completed")
        log_info("✓ Windows特定的最终化完成", lang="zh")

    @staticmethod
    def _finalize_unix() -> None:
        """Unix-like平台的最终化操作"""
        log_info("✓ Unix-specific finalization completed")
        log_info("✓ Unix特定的最终化完成", lang="zh")
