"""Gitignore template manager."""

import os
import shutil
from pathlib import Path

from py_wlcommands.utils.logging import log_info


class GitignoreManager:
    """Manager for .gitignore template operations."""

    def copy_gitignore_template(self) -> None:
        """Copy .gitignore template from vendors to project root.

        Copies the .gitignore template from the vendors directory to the
        current working directory if no .gitignore file already exists.
        """
        gitignore_path = Path(".gitignore")

        # Only copy if .gitignore doesn't exist and not in test environment
        if gitignore_path.exists() or os.environ.get("PYTEST_CURRENT_TEST"):
            return

        try:
            # Calculate path to vendors/git/.gitignore relative to this file
            template_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "vendors"
                / "git"
                / ".gitignore"
            )

            log_info(f"Looking for .gitignore template at: {template_path}")

            if template_path.exists():
                shutil.copy2(template_path, ".gitignore")
                log_info("✓ .gitignore template copied successfully")
                log_info("✓ .gitignore 模板复制成功", lang="zh")
            else:
                log_info(f"Warning: .gitignore template not found at {template_path}")
                log_info(f"警告: 未找到 .gitignore 模板 {template_path}", lang="zh")
        except Exception as e:
            log_info(f"Warning: Failed to copy .gitignore template: {e}")
            log_info(f"警告: 复制 .gitignore 模板失败: {e}", lang="zh")
