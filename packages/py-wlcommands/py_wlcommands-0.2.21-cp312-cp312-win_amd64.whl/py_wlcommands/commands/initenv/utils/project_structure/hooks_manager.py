"""Git hooks manager utilities for project structure setup."""

import os
import re
import shutil
import subprocess
from pathlib import Path

from .....utils.logging import log_info
from ..config_manager import ConfigManager


def _check_git_bash_installed() -> None:
    """
    Check if Git Bash is installed on Windows.

    Git Bash is required for Git hooks to work properly on Windows.
    If Git Bash is not found, display a warning message.
    If Git Bash is found but not in PATH, add its directory to the project environment.
    """
    try:
        # Try to find git bash in common locations
        common_paths = [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
            r"C:\Git\bin\bash.exe",
        ]

        # Also check PATH environment variable
        path_env = os.environ.get("PATH", "")

        git_bash_path = None

        # Check common paths
        for path in common_paths:
            if Path(path).exists():
                git_bash_path = path
                break

        # If not found, check PATH
        if not git_bash_path:
            for path_dir in path_env.split(os.pathsep):
                bash_path = Path(path_dir) / "bash.exe"
                if bash_path.exists():
                    git_bash_path = str(bash_path)
                    break

        # If Git Bash is found
        if git_bash_path:
            git_bash_dir = str(Path(git_bash_path).parent)

            # Check if Git Bash directory is already in PATH
            if git_bash_dir not in path_env:
                log_info(f"✓ Git Bash found at: {git_bash_path}")
                log_info(f"✓ Git Bash 位于: {git_bash_path}", lang="zh")

                # Add Git Bash directory to project environment
                # This ensures hooks can find Git Bash during execution
                os.environ["PATH"] = f"{git_bash_dir}{os.pathsep}{path_env}"
                log_info(f"✓ Added Git Bash directory to PATH: {git_bash_dir}")
                log_info(f"✓ 将Git Bash目录添加到PATH: {git_bash_dir}", lang="zh")
            else:
                log_info(f"✓ Git Bash already in PATH: {git_bash_path}")
                log_info(f"✓ Git Bash 已在PATH中: {git_bash_path}", lang="zh")

        # If still not found, display warning
        if not git_bash_path:
            log_info("Warning: Git Bash not found on Windows.")
            log_info("警告: 在Windows上未找到Git Bash。")
            log_info("Git Bash is required for Git hooks to work properly on Windows.")
            log_info("在Windows上，Git钩子需要Git Bash才能正常工作。")
            log_info("Please download and install Git Bash from: https://git-scm.com/")
            log_info("请从以下地址下载并安装Git Bash: https://git-scm.com/")
            log_info("After installation, please restart your terminal and try again.")
            log_info("安装完成后，请重启终端并再次尝试。")
    except Exception as e:
        log_info(f"Warning: Error checking for Git Bash: {e}")
        log_info(f"警告: 检查Git Bash时出错: {e}")


def _get_hooks_paths(config_manager: ConfigManager) -> tuple[Path, Path]:
    """Get hooks source and destination paths."""
    hooks_dest = Path(".wl") / "hooks"
    hooks_dest.mkdir(parents=True, exist_ok=True)

    # Use Unix-style hooks for all platforms (Git Bash will handle Windows execution)
    hooks_src = config_manager.get_vendor_config_path("hooks/unix")

    # Fallback to the root hooks directory if Unix directory doesn't exist
    if not hooks_src.exists():
        hooks_src = config_manager.get_vendor_config_path("hooks")

    return hooks_src, hooks_dest


def _copy_main_hook(hook_file: Path, hooks_src: Path, hooks_dest: Path) -> None:
    """Copy main hook files with legacy support."""
    legacy_hook_path = hooks_src / f"{hook_file.name}.legacy"
    dest_hook_path = hooks_dest / hook_file.name

    if legacy_hook_path.exists():
        # Copy legacy Bash version as the main hook
        shutil.copy2(legacy_hook_path, dest_hook_path)
    else:
        # Fallback to the default version
        shutil.copy2(hook_file, dest_hook_path)

    # Make executable
    dest_hook_path.chmod(0o755)


def _copy_support_file(hook_file: Path, hooks_dest: Path) -> None:
    """Copy support files and set permissions if needed."""
    dest_file = hooks_dest / hook_file.name
    shutil.copy2(hook_file, dest_file)

    # Make executable if it's a script file
    if hook_file.name in ["check_lockfile.sh", "check_lockfile.py"]:
        dest_file.chmod(0o755)


def _copy_check_lockfile(hooks_src: Path, hooks_dest: Path) -> None:
    """Copy check_lockfile.py separately if it exists."""
    check_lockfile_py = hooks_src / "check_lockfile.py"
    if check_lockfile_py.exists():
        dest_check_lockfile = hooks_dest / "check_lockfile.py"
        shutil.copy2(check_lockfile_py, dest_check_lockfile)
        dest_check_lockfile.chmod(0o755)


def _copy_hook_files(hooks_src: Path, hooks_dest: Path) -> None:
    """Copy all hook files from source to destination."""
    if not hooks_src.exists():
        return

    # Copy all files from vendors/hooks/unix to .wl/hooks
    for hook_file in hooks_src.iterdir():
        # Skip sample files
        if hook_file.is_file() and not hook_file.name.endswith(".sample"):
            # Handle main hooks specially
            if hook_file.name in ["pre-commit", "pre-push"]:
                _copy_main_hook(hook_file, hooks_src, hooks_dest)
            elif hook_file.name in ["pre-commit.py", "pre-push.py"]:
                # Skip Python wrapper scripts
                continue
            else:
                # Copy other files normally
                _copy_support_file(hook_file, hooks_dest)

    # Copy check_lockfile.py separately since it's needed for pre-commit hooks
    _copy_check_lockfile(hooks_src, hooks_dest)


def _configure_git_hooks_path() -> None:
    """Configure Git to use the custom hooks directory."""
    try:
        hooks_dir = os.path.abspath(".wl/hooks")
        subprocess.run(
            ["git", "config", "core.hooksPath", hooks_dir],
            check=True,
            capture_output=False,
        )
        log_info(f"✓ Configured Git to use custom hooks directory: {hooks_dir}")
        log_info(f"✓ 配置Git使用自定义钩子目录: {hooks_dir}", lang="zh")
    except subprocess.CalledProcessError as e:
        log_info(f"Warning: Failed to configure custom hooks directory: {e}")
        log_info(f"警告: 配置自定义钩子目录失败: {e}", lang="zh")
    except Exception as e:
        log_info(f"Warning: Failed to configure custom hooks directory: {e}")
        log_info(f"警告: 配置自定义钩子目录失败: {e}", lang="zh")


def _log_missing_hooks_directory(config_manager: ConfigManager) -> None:
    """Log warning if hooks directory is missing."""
    hooks_dir_path = config_manager.get_vendor_config_path("hooks/unix")
    if not hooks_dir_path.exists():
        log_info(f"  Warning: Hooks template directory not found at {hooks_dir_path}")
        log_info(f"  警告: 未找到hooks模板目录 {hooks_dir_path}", lang="zh")


def _copy_and_configure_hooks() -> None:
    """Copy and configure git hooks for the project.

    This function:
    1. Copies hook templates from vendors/hooks to .wl/hooks
    2. Configures hooks for the current platform
    3. Sets core.hooksPath to .wl/hooks
    """
    config_manager = ConfigManager()

    # Check for Git Bash on Windows
    if os.name == "nt":
        _check_git_bash_installed()

    # Get hooks paths
    hooks_src, hooks_dest = _get_hooks_paths(config_manager)

    # Copy hook files
    _copy_hook_files(hooks_src, hooks_dest)

    # Configure Git to use the hooks directory
    _configure_git_hooks_path()

    # Check if hooks directory exists and log warning if not
    _log_missing_hooks_directory(config_manager)
