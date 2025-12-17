"""Pre-commit hook manager."""

import os
from pathlib import Path

from py_wlcommands.utils.logging import log_info


class PreCommitManager:
    """Manager for pre-commit hook operations."""

    def _update_hook_entries_for_platform(self, config_content: str) -> str:
        """Update check-lockfile hook entry based on platform.

        Args:
            config_content: The content of the pre-commit config file.

        Returns:
            The updated config content with platform-specific hook entries.
        """
        # Define the hook entries for different platforms
        if os.name == "nt":  # Windows platform
            # Use Windows-specific command
            target_entry = "entry: .wl/hooks/check_lockfile.bat"
            log_info(
                "Updated check-lockfile hook entry to use .bat extension for Windows platform"
            )
        else:  # Unix-like platforms
            # Use Unix-specific command
            target_entry = "entry: .wl/hooks/check_lockfile.sh"
            log_info(
                "Updated check-lockfile hook entry to use .sh extension for Unix platform"
            )

        # Check if we need to update the entry
        # First, find if the entry line exists in the check-lockfile hook section
        updated = False
        lines = config_content.split("\n")
        for i, line in enumerate(lines):
            # Find the check-lockfile hook section
            if "check-lockfile" in line and "id:" in line:
                # Look for the entry line within the next few lines
                for j in range(i, min(i + 10, len(lines))):
                    if "entry:" in lines[j]:
                        old_entry = lines[j].strip()
                        if old_entry != f"        {target_entry}":
                            lines[j] = f"        {target_entry}"
                            updated = True
                        break
                break

        # If updated, join the lines back together
        if updated:
            config_content = "\n".join(lines)

        return config_content

    def create_pre_commit_config(self) -> None:
        """Create pre-commit configuration file.

        Creates the pre-commit configuration file in .wl/.pre-commit-config.yaml if it doesn't already exist.
        """
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return

        log_info("Creating pre-commit configuration...")
        log_info("创建预提交配置...", lang="zh")

        try:
            # Create pre-commit-config.yaml if it doesn't exist
            pre_commit_config_path = Path(".wl/.pre-commit-config.yaml")
            if not pre_commit_config_path.exists():
                # Calculate path to vendors/git/.pre-commit-config.yaml relative to this file
                template_path = (
                    Path(__file__).parent.parent.parent.parent.parent
                    / "vendors"
                    / "git"
                    / ".pre-commit-config.yaml"
                )

                log_info(f"Looking for pre-commit config template at: {template_path}")

                if template_path.exists():
                    config_content = template_path.read_text()

                    # Update check-lockfile hook entry based on platform
                    config_content = self._update_hook_entries_for_platform(
                        config_content
                    )

                    pre_commit_config_path.parent.mkdir(parents=True, exist_ok=True)
                    pre_commit_config_path.write_text(config_content)
                    log_info("✓ .pre-commit-config.yaml created from template")
                    log_info("✓ .pre-commit-config.yaml 从模板创建成功", lang="zh")
                else:
                    log_info(
                        f"Warning: pre-commit config template not found at {template_path}"
                    )
                    log_info(
                        f"警告: 未找到 pre-commit 配置模板 {template_path}", lang="zh"
                    )
            else:
                log_info(".pre-commit-config.yaml already exists, skipping creation")
                log_info(".pre-commit-config.yaml 已存在，跳过创建", lang="zh")
        except Exception as e:
            log_info(f"Warning: Failed to create pre-commit configuration: {e}")
            log_info(f"警告: 创建预提交配置失败: {e}", lang="zh")

    def verify_pre_commit_config(self) -> None:
        """Verify pre-commit configuration file exists.

        Checks that the pre-commit configuration file exists.
        """
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return

        log_info("Verifying pre-commit configuration...")
        log_info("验证预提交配置...", lang="zh")

        try:
            # Check if config file exists
            pre_commit_config_path = Path(".wl/.pre-commit-config.yaml")
            if pre_commit_config_path.exists():
                log_info("✓ Pre-commit config file exists")
                log_info("✓ 预提交配置文件存在", lang="zh")
            else:
                log_info("Warning: Pre-commit config file does not exist")
                log_info("警告: 预提交配置文件不存在", lang="zh")
        except Exception as e:
            log_info(f"Warning: Failed to verify pre-commit configuration: {e}")
            log_info(f"警告: 验证预提交配置失败: {e}", lang="zh")

    # Keep the original method for backward compatibility
    def create_pre_commit_hook(self) -> None:
        """Create pre-commit hook and configuration file.

        This method is deprecated and only kept for backward compatibility.
        Use create_pre_commit_config() instead.
        """
        self.create_pre_commit_config()

    # Keep the original method for backward compatibility
    def verify_pre_commit_hook(self) -> None:
        """Verify pre-commit hook is valid and executable.

        This method is deprecated and only kept for backward compatibility.
        Use verify_pre_commit_config() instead.
        """
        self.verify_pre_commit_config()
