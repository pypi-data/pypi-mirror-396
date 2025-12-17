"""工作流初始化处理器"""

from py_wlcommands.commands.initenv.utils.git_initializer import GitInitializer
from py_wlcommands.commands.initenv.utils.platform_adapter import PlatformAdapter
from py_wlcommands.utils.logging import log_info


class InitWorkHandler:
    """处理工作流初始化的类"""

    @staticmethod
    def initialize(work_type: str) -> None:
        """
        初始化Git Flow工作环境

        Args:
            work_type: 工作类型 (feature, fix, hotfix, release)
        """
        log_info(f"=== Starting Git Flow Work Initialization for {work_type} ===")
        log_info(f"=== 开始 Git Flow 工作初始化，类型：{work_type} ===", lang="zh")

        # 检测平台
        env = PlatformAdapter.get_env()
        git_initializer = GitInitializer(env)

        # 设置Git Flow分支
        InitWorkHandler._setup_git_flow_branch(git_initializer, work_type)

        # 提供提交格式指南
        CommitFormatGuide.show()

        log_info(f"Git Flow Work Initialization for {work_type} completed!")
        log_info(f"Git Flow 工作初始化，类型：{work_type} 已完成！", lang="zh")

    @staticmethod
    def _setup_git_flow_branch(git_initializer: GitInitializer, work_type: str) -> None:
        """
        根据工作类型设置Git Flow分支

        Args:
            git_initializer: Git初始化器实例
            work_type: 工作类型
        """
        log_info(f"Setting up Git Flow branch for {work_type}...")
        log_info(f"正在设置 {work_type} 类型的 Git Flow 分支...", lang="zh")

        # 如果Git仓库不存在，则初始化
        git_initializer.initialize()

        # 根据工作类型设置Git Flow分支
        git_initializer.setup_git_flow_branches(work_type)


class CommitFormatGuide:
    """提交格式指南工具类"""

    @staticmethod
    def show() -> None:
        """
        向用户提供提交格式指南
        """
        log_info("\n=== Commit Format Guide ===")
        log_info("请使用以下格式提交代码：")
        log_info("\n示例：")
        log_info('  git commit -m "feat: add user authentication feature"')
        log_info('  git commit -m "fix: resolve login form validation issue"')
        log_info('  git commit -m "hotfix: patch security vulnerability"')
        log_info('  git commit -m "docs: update README with usage examples"')
        log_info("\n格式说明：")
        log_info("  <类型>: <简短描述>")
        log_info("\n类型列表：")
        log_info("  feat: 新功能")
        log_info("  fix: Bug 修复")
        log_info("  hotfix: 紧急修复")
        log_info("  docs: 文档更新")
        log_info("  style: 代码格式（不影响功能）")
        log_info("  refactor: 代码重构（不影响功能）")
        log_info("  test: 添加或修改测试")
        log_info("  chore: 构建或工具更新")
