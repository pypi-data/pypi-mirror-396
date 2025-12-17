"""Project structure setup handler."""

import os
import re
import shutil
from pathlib import Path

from .....utils.logging import log_info
from .....utils.workspace_detector.venv_resolver import get_active_venv_path_str
from ..config_manager import ConfigManager
from ..log_manager import performance_monitor


class ProjectStructureSetup:
    """Project structure setup handler."""

    def __init__(self) -> None:
        self.config_manager = ConfigManager()

    @performance_monitor
    def setup(self, project_name: str) -> None:
        """Setup project structure."""
        # Create main project structure
        directories = [
            "src",
            f"src/{project_name}",
            f"src/{project_name}/lib",  # 添加lib目录以支持Rust扩展
            "tests",
            "docs",
            "examples",
            "rust",
            ".wl",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            # Create __init__.py files for Python packages
            if directory.startswith("src/") or directory == "tests":
                init_file = Path(directory) / "__init__.py"
                if not init_file.exists():
                    init_file.touch()

        # Create README.md if it doesn't exist or is empty
        readme_file = Path("README.md")
        should_create_readme = (
            not readme_file.exists()
            or readme_file.read_text(encoding="utf-8").strip() == ""
        )
        if should_create_readme:
            self._copy_and_customize_readme(project_name)

        # Generate SOP files for Rust-Python integration
        self._generate_sop_files(project_name)

        # Copy Rust example files
        self._copy_rust_example_files(project_name)

        # Generate configuration files in .wl directory
        self._generate_wl_configs()

        log_info("✓ Project structure created successfully")
        log_info("✓ 项目结构创建成功", lang="zh")

    def _copy_and_customize_readme(self, project_name: str) -> None:
        """Copy README template and customize it for the project."""
        try:
            # Calculate path to vendors/readme/README.md relative to this file
            template_path = self.config_manager.get_vendor_config_path(
                "readme/README.md"
            )

            if template_path.exists():
                # Read the template
                with open(template_path, encoding="utf-8") as f:
                    template_content = f.read()

                # Customize the template
                customized_content = template_content.format(
                    project_name=project_name,
                    project_description=f"{project_name} - A Python project",
                    cli_command="wl",  # Default CLI command
                )

                # Write to project README.md
                with open("README.md", "w", encoding="utf-8") as f:
                    f.write(customized_content)

                log_info(
                    f"✓ README.md template copied and customized for: {project_name}"
                )
                log_info(f"✓ README.md 模板复制并定制化完成: {project_name}", lang="zh")
            else:
                # Fallback to simple README if template doesn't exist
                with open("README.md", "w", encoding="utf-8") as f:
                    f.write(f"# {project_name}\n")
                log_info(
                    f"✓ Created simple README.md with project name: {project_name}"
                )
                log_info(f"✓ 创建简单 README.md，项目名: {project_name}", lang="zh")
        except Exception as e:
            # Fallback to simple README if customization fails
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(f"# {project_name}\n")
            log_info(f"Warning: Failed to customize README.md, created simple one: {e}")
            log_info(f"警告: 定制 README.md 失败，创建简单版本: {e}", lang="zh")

    def _generate_wl_configs(self) -> None:
        """Generate configuration files in .wl directory."""
        wl_dir = Path(".wl")
        log_dir = wl_dir / "log"
        config_file = wl_dir / "config.json"

        # Create log directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)
        log_info("✓ Created .wl/log directory")
        log_info("✓ 创建 .wl/log 目录", lang="zh")

        # Create default config file if it doesn't exist
        if not config_file.exists():
            try:
                # Create default config using the global config manager
                from .....utils.config import get_config_manager

                config_manager = get_config_manager()
                # Just accessing the config manager will create the default config file
                config = config_manager.get_all()
                log_info(f"✓ Created default config file at {config_file}")
                log_info(f"✓ 在 {config_file} 创建默认配置文件", lang="zh")
            except Exception as e:
                log_info(f"Warning: Failed to create default config file: {e}")
                log_info(f"警告: 创建默认配置文件失败: {e}", lang="zh")

        # Copy .codespellrc from vendors/config
        codespell_src = self.config_manager.get_vendor_config_path(
            "config/.codespellrc"
        )
        codespell_dest = wl_dir / ".codespellrc"
        if not codespell_dest.exists() and codespell_src.exists():
            shutil.copy2(codespell_src, codespell_dest)
            log_info("✓ Copied .wl/.codespellrc from template")
            log_info("✓ 从模板复制 .wl/.codespellrc", lang="zh")

        # Copy .pre-commit-config.yaml from vendors/git
        precommit_src = self.config_manager.get_vendor_config_path(
            "git/.pre-commit-config.yaml"
        )
        precommit_dest = wl_dir / ".pre-commit-config.yaml"
        root_precommit = Path(".pre-commit-config.yaml")

        # Ensure .wl/.pre-commit-config.yaml exists
        if not precommit_dest.exists() and precommit_src.exists():
            shutil.copy2(precommit_src, precommit_dest)
            log_info("✓ Copied .wl/.pre-commit-config.yaml from template")
            log_info("✓ 从模板复制 .wl/.pre-commit-config.yaml", lang="zh")

        # Create hardlink to project root if it doesn't exist
        if not root_precommit.exists() and precommit_dest.exists():
            try:
                os.link(precommit_dest, root_precommit)
                log_info(
                    "✓ Created hardlink to .pre-commit-config.yaml in project root"
                )
                log_info("✓ 在项目根目录创建 .pre-commit-config.yaml 硬链接", lang="zh")
            except Exception as e:
                log_info(f"Warning: Failed to create hardlink: {e}")
                log_info(f"警告: 创建硬链接失败: {e}", lang="zh")
                # Fallback: Copy the file if hardlink fails
                shutil.copy2(precommit_dest, root_precommit)
                log_info("✓ Copied .pre-commit-config.yaml to project root (fallback)")
                log_info(
                    "✓ 复制 .pre-commit-config.yaml 到项目根目录 (备用方案)", lang="zh"
                )

        # Copy and configure git hooks from vendors/hooks to .wl/hooks
        from .hooks_manager import _copy_and_configure_hooks

        _copy_and_configure_hooks()

    def _generate_sop_files(self, project_name: str) -> None:
        """Generate SOP files for Rust-Python integration."""
        try:
            # Generate Rust README SOP
            rust_readme_src = self.config_manager.get_vendor_config_path(
                "sop_doc/rust-readme.md"
            )
            rust_readme_dest = Path("rust/README.md")
            if rust_readme_src.exists() and not rust_readme_dest.exists():
                shutil.copy2(rust_readme_src, rust_readme_dest)
                log_info("✓ Generated Rust-Python integration SOP in rust/README.md")
                log_info("✓ 在 rust/README.md 生成 Rust-Python 集成 SOP", lang="zh")

            # Generate Python SOP for Rust extension
            python_sop_src = self.config_manager.get_vendor_config_path(
                "sop_doc/python-sop.md"
            )
            python_sop_dest = Path(f"src/{project_name}/lib/sop.md")
            if python_sop_src.exists() and not python_sop_dest.exists():
                shutil.copy2(python_sop_src, python_sop_dest)
                log_info(
                    f"✓ Generated Python SOP for Rust extension in src/{project_name}/lib/sop.md"
                )
                log_info(
                    f"✓ 在 src/{project_name}/lib/sop.md 生成 Python 引入 Rust 扩展 SOP",
                    lang="zh",
                )
        except Exception as e:
            log_info(f"Warning: Failed to generate SOP files: {e}")
            log_info(f"警告: 生成 SOP 文件失败: {e}", lang="zh")

    def _copy_rust_example_files(self, project_name: str) -> None:
        """Copy Rust example files from vendors to project."""
        try:
            # Copy lib files
            vendor_lib_dir = self.config_manager.get_vendor_config_path("rust/lib")
            target_lib_dir = Path(f"src/{project_name}/lib")

            for file_name in ["__init__.py", "rust_utils.py"]:
                src_file = vendor_lib_dir / file_name
                dest_file = target_lib_dir / file_name
                if src_file.exists() and not dest_file.exists():
                    shutil.copy2(src_file, dest_file)
                    log_info(f"✓ Copied {file_name} to {target_lib_dir}")
                    log_info(f"✓ 复制 {file_name} 到 {target_lib_dir}", lang="zh")

            # Copy test file
            vendor_test_dir = self.config_manager.get_vendor_config_path("rust/tests")
            target_test_dir = Path("tests")

            test_file = "test_rust_fallback.py"
            src_test = vendor_test_dir / test_file
            dest_test = target_test_dir / test_file
            if src_test.exists() and not dest_test.exists():
                shutil.copy2(src_test, dest_test)
                log_info(f"✓ Copied {test_file} to {target_test_dir}")
                log_info(f"✓ 复制 {test_file} 到 {target_test_dir}", lang="zh")

        except Exception as e:
            log_info(f"Warning: Failed to copy Rust example files: {e}")
            log_info(f"警告: 复制 Rust 示例文件失败: {e}", lang="zh")
