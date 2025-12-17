"""Directory creator utilities for project structure setup."""

from pathlib import Path

from .....utils.logging import log_info
from ..config_manager import ConfigManager


def _create_required_directories(normalized_name: str) -> None:
    """Create required directories for the project."""
    required_dirs = [
        Path("src"),
        Path("src") / normalized_name,
        Path("src") / normalized_name / "lib",  # 添加lib目录以支持Rust扩展
        Path("rust"),
        Path("tests"),
        Path("docs"),
        Path("examples"),
        Path("dist"),
    ]

    # Create directories
    for dir_path in required_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)


def _create_init_files(normalized_name: str) -> None:
    """Create required __init__.py files for the project."""
    required_inits = [
        Path("src") / normalized_name / "__init__.py",
        Path("tests") / "__init__.py",
    ]

    for init_file in required_inits:
        if init_file.parent.exists():
            init_file.touch(exist_ok=True)


def _create_readme(project_name: str) -> None:
    """Create README.md file for the project."""
    readme_file = Path("README.md")
    should_create_readme = (
        not readme_file.exists()
        or readme_file.read_text(encoding="utf-8").strip() == ""
    )

    if should_create_readme:
        config_manager = ConfigManager()
        # Calculate path to vendors/readme/README.md relative to this file
        template_path = config_manager.get_vendor_config_path("readme/README.md")

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
        else:
            # Fallback to simple README if template doesn't exist
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(f"# {project_name}\n")


def setup_project_structure(project_name: str) -> None:
    """Setup project structure manually."""
    # Normalize project name
    normalized_name = project_name.replace("-", "_")

    log_info(f"Setting up project structure for '{project_name}'...")
    log_info(f"为 '{project_name}' 设置项目结构...", lang="zh")

    # Create required directories
    _create_required_directories(normalized_name)

    # Create required __init__.py files
    _create_init_files(normalized_name)

    # Create README.md if needed
    _create_readme(project_name)

    # Copy and configure git hooks
    from .hooks_manager import _copy_and_configure_hooks

    _copy_and_configure_hooks()

    log_info("✓ Project structure set up successfully")
    log_info("✓ 项目结构设置成功", lang="zh")
