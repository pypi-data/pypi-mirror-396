"""Custom exceptions for initenv commands."""

import shutil
from pathlib import Path

from ....utils.logging import log_info
from .exceptions import RustInitializationError
from .log_manager import performance_monitor
from .pyproject_generator import clean_cargo_name  # Import the cleaning function


class RustInitializer:
    """Rust environment initializer."""

    def __init__(self) -> None:
        pass

    @performance_monitor
    def initialize(self) -> None:
        """Initialize Rust environment."""
        rust_dir = Path("rust")

        # Create rust directory if it doesn't exist
        if not rust_dir.exists():
            log_info("Creating rust directory...")
            log_info("创建rust目录...", lang="zh")
            rust_dir.mkdir(exist_ok=True)

        # Check if Cargo.toml exists
        cargo_toml_path = rust_dir / "Cargo.toml"
        if cargo_toml_path.exists():
            log_info("Cargo.toml already exists, skipping creation")
            log_info("Cargo.toml 已存在，跳过创建", lang="zh")
            return

        # Use project template files instead of cargo init
        log_info("Initializing Rust project with project template...")
        log_info("使用项目模板初始化Rust项目...", lang="zh")
        try:
            # Get the template directory path
            # Calculate path to vendors/rust directory relative to this file
            # File is in src/py_wlcommands/commands/initenv/utils/
            # vendors dir is in src/py_wlcommands/
            # So we need to go up 4 levels
            template_dir = (
                Path(__file__).parent.parent.parent.parent / "vendors" / "rust"
            )

            log_info(f"Template directory: {template_dir}")

            if not template_dir.exists():
                raise RustInitializationError(
                    f"Rust template directory not found: {template_dir}"
                )

            # Get project name from current directory
            project_name = Path.cwd().name

            # Copy template files to rust directory
            for item in template_dir.iterdir():
                dest_path = rust_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest_path, dirs_exist_ok=True)
                else:
                    # Special handling for Cargo.toml to replace project name
                    if item.name == "Cargo.toml":
                        self._copy_and_update_cargo_toml(item, dest_path, project_name)
                    else:
                        shutil.copy2(item, dest_path)

            # Update lib.rs with the correct module name
            lib_rs_path = rust_dir / "src" / "lib.rs"
            if lib_rs_path.exists():
                self._update_lib_rs(lib_rs_path, project_name)

            log_info("✓ Rust project initialized successfully with template")
            log_info("✓ 使用模板成功初始化Rust项目", lang="zh")
        except Exception as e:
            raise RustInitializationError(f"Failed to initialize Rust project: {e}")

    def _copy_and_update_cargo_toml(
        self, source: Path, dest: Path, project_name: str
    ) -> None:
        """Copy Cargo.toml template and update project name."""
        # Read the template file
        with open(source, encoding="utf-8") as f:
            content = f.read()

        # Clean the project name to be a valid Cargo name
        cleaned_project_name = clean_cargo_name(project_name)
        # Ensure the library name uses underscores, not hyphens
        lib_name = cleaned_project_name + "_native"

        # Warn users if their project name contains hyphens
        if "-" in project_name:
            log_info(
                "Warning: Project name contains hyphens which are not allowed in Rust library names."
            )
            log_info("         Converting to underscores for Rust compatibility.")
            log_info("警告: 项目名称包含连字符，这在Rust库名称中是不允许的。")
            log_info("      已转换为下划线以确保与Rust兼容。", lang="zh")

        # Replace the template project name with actual project name
        # Replace both the package name and the lib name
        updated_content = content.replace("py_wlcommands_native", lib_name)
        # Also replace in the [lib] section to ensure library name is correct
        updated_content = updated_content.replace(
            'name = "py_wlcommands_native"', f'name = "{lib_name}"'
        )

        # Write the updated content to destination
        with open(dest, "w", encoding="utf-8") as f:
            f.write(updated_content)

    def _update_lib_rs(self, lib_rs_path: Path, project_name: str) -> None:
        """Update lib.rs with the correct module name."""
        # Read the template file
        with open(lib_rs_path, encoding="utf-8") as f:
            content = f.read()

        # Clean the project name to be a valid Cargo name
        cleaned_project_name = clean_cargo_name(project_name)
        # Ensure the library name uses underscores, not hyphens
        lib_name = cleaned_project_name + "_native"

        # Warn users if their project name contains hyphens
        if "-" in project_name:
            log_info(
                "Warning: Project name contains hyphens which are not allowed in Rust library names."
            )
            log_info("         Converting to underscores for Rust compatibility.")
            log_info("警告: 项目名称包含连字符，这在Rust库名称中是不允许的。")
            log_info("      已转换为下划线以确保与Rust兼容。", lang="zh")

        # Replace the template project name with actual project name in lib.rs
        updated_content = content.replace("py_wlcommands_native", lib_name)
        with open(lib_rs_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
