"""提供Git提交格式指南的模块"""

from ...utils.logging import log_info


class CommitFormatGuide:
    """Git提交格式指南类"""

    @staticmethod
    def show_guide() -> None:
        """显示提交格式指南"""
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
