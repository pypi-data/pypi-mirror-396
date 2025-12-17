"""
Build utilities for WL Commands.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info
from ...utils.subprocess import run_command
from ...utils.workspace_detector import WorkspaceDetectionError, WorkspaceDetector
from ..format.python_formatter import generate_type_stubs


def is_rust_enabled() -> bool:
    """
    Check if Rust is enabled for this project.

    Returns:
        bool: True if Rust is enabled, False otherwise.
    """
    rust_dir = os.path.join(os.getcwd(), "rust")
    cargo_toml = os.path.join(rust_dir, "Cargo.toml")
    return os.path.exists(cargo_toml)


def _create_venv() -> None:
    """Create virtual environment using uv."""
    try:
        # Use uv to create virtual environment
        cmd = ["uv", "venv"]
        subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True,
        )
        log_info("✓ Virtual environment created successfully")
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to create virtual environment: {e}")
        raise CommandError(f"Failed to create virtual environment: {e}")
    except Exception as e:
        log_error(f"Unexpected error creating virtual environment: {e}")
        raise CommandError(f"Failed to create virtual environment: {e}")


def _resolve_python(detector: WorkspaceDetector) -> tuple[str | None, bool]:
    is_workspace = detector.detect(Path.cwd())
    if not is_workspace:
        log_info("Not in uv workspace environment")
        return "python", False
    log_info("✓ uv workspace environment detected")
    venv_root = detector.get_venv_path(Path.cwd())
    if venv_root is None:
        try:
            venv_str = detector.get_active_venv_path_str(Path.cwd())
            venv_root = Path(venv_str)
        except Exception:
            venv_root = None
    if venv_root is None:
        log_info("No venv found, creating local .venv for build...")
        _create_venv()
        venv_root = Path(".venv")
    if sys.platform.startswith("win"):
        return str((venv_root / "Scripts" / "python.exe").resolve()), True
    return str((venv_root / "bin" / "python").resolve()), True


def _generate_and_copy_stubs() -> None:
    try:
        root = Path.cwd()
        src_path = root / "src"
        typings_path = root / "typings"
        if not src_path.exists():
            return
        log_info(f"Generating type stubs for {src_path} -> {typings_path}")
        generate_type_stubs(
            str(src_path), str(typings_path), os.environ.copy(), quiet=False
        )
        log_info("✓ Type stubs generated")
        package_root = src_path / "py_wlcommands"
        stub_root = typings_path / "py_wlcommands"
        if stub_root.exists():
            for pyi in stub_root.rglob("*.pyi"):
                rel = pyi.relative_to(stub_root)
                dest = package_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pyi, dest)
            log_info("✓ Type stubs copied into package source")
        else:
            for pyi in typings_path.rglob("*.pyi"):
                try:
                    parts = list(pyi.parts)
                    if "py_wlcommands" in parts:
                        idx = parts.index("py_wlcommands")
                        rel = Path(*parts[idx + 1 :])
                        dest = package_root / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(pyi, dest)
                except Exception:
                    continue
    except Exception as e:
        log_error(f"Failed to generate type stubs: {e}")


def _run_maturin_build(python_executable: str | None) -> None:
    command = ["maturin", "build", "--release", "--out", "dist"]
    if python_executable:
        command.extend(["-i", python_executable])
    log_info(f"Trying to build with: {' '.join(command)}")
    subprocess.run(command, check=True, capture_output=False, text=True)


def _cleanup_after_build(is_workspace: bool) -> None:
    try:
        if is_workspace and Path(".venv").exists():
            log_info("In uv workspace, removing .venv directory...")
            shutil.rmtree(".venv")
            log_info("✓ .venv directory removed")
        root = Path.cwd()
        typings_path = root / "typings"
        if typings_path.exists():
            shutil.rmtree(typings_path, ignore_errors=True)
            log_info("✓ typings directory removed")
        src_path = root / "src"
        if src_path.exists():
            removed = 0
            for p in src_path.rglob("*.pyi"):
                try:
                    p.unlink()
                    removed += 1
                except Exception:
                    pass
            if removed:
                log_info(f"✓ Removed {removed} .pyi files from src")
    except Exception as e:
        log_error(f"Failed to cleanup stubs: {e}")


def build_project_full() -> None:
    rust_enabled = is_rust_enabled()

    try:
        if rust_enabled:
            log_info("Using maturin build for full compilation...")
            log_info("使用 maturin build 进行完整编译...", lang="zh")
            detector = WorkspaceDetector()
            python_executable, is_workspace = _resolve_python(detector)
            _generate_and_copy_stubs()
            _run_maturin_build(python_executable)
            _cleanup_after_build(is_workspace)
        else:
            log_info(
                "Pure Python project, using uv pip install -e . for installation..."
            )
            log_info("纯 Python 项目，使用 uv pip install -e . 进行安装...", lang="zh")
            run_command(
                ["uv", "pip", "install", "--link-mode=copy", "-e", "."],
                capture_output=False,
            )

        log_info("✓ Full build completed successfully")
        log_info("✓ 完整构建成功完成", lang="zh")
    except subprocess.CalledProcessError as e:
        log_error(f"Full build failed: {e}")
        log_error(f"完整构建失败: {e}", lang="zh")
        raise CommandError(f"Full build failed with return code {e.returncode}")
    except WorkspaceDetectionError as e:
        log_error(f"Workspace detection error: {e}")
        log_error(f"工作空间检测错误: {e}", lang="zh")
        raise CommandError(f"Full build failed: {e}")
    except Exception as e:
        log_error(f"Unexpected error during full build: {e}")
        log_error(f"完整构建过程中出现意外错误: {e}", lang="zh")
        raise CommandError(f"Full build failed: {e}")


def build_windows() -> None:
    """Build the project on Windows."""
    rust_enabled = is_rust_enabled()

    try:
        if rust_enabled:
            log_info("Using maturin develop to build and install editable package...")
            log_info("使用 maturin develop 构建和安装可编辑包...", lang="zh")
            # 使用maturin的原生增量编译功能
            run_command(["maturin", "develop", "--skip-install"], capture_output=False)
        else:
            log_info(
                "Pure Python project, using uv pip install -e . for installation..."
            )
            log_info("纯 Python 项目，使用 uv pip install -e . 进行安装...", lang="zh")
            run_command(
                ["uv", "pip", "install", "--link-mode=copy", "-e", "."],
                capture_output=False,
            )

        log_info("✓ Build completed successfully")
        log_info("✓ 构建成功完成", lang="zh")
    except CommandError as e:
        log_error(f"Build failed: {e}")
        log_error(f"构建失败: {e}", lang="zh")
        raise
    except Exception as e:
        log_error(f"Unexpected error during build: {e}")
        log_error(f"构建过程中出现意外错误: {e}", lang="zh")
        raise CommandError(f"Build failed: {e}")


def build_unix() -> None:
    """Build the project on Unix-like systems."""
    rust_enabled = is_rust_enabled()

    try:
        if rust_enabled:
            log_info("Using maturin develop to build and install editable package...")
            log_info("使用 maturin develop 构建和安装可编辑包...", lang="zh")
            # 使用maturin的原生增量编译功能
            run_command(["maturin", "develop", "--skip-install"], capture_output=False)
        else:
            log_info(
                "Pure Python project, using uv pip install -e . for installation..."
            )
            log_info("纯 Python 项目，使用 uv pip install -e . 进行安装...", lang="zh")
            run_command(
                ["uv", "pip", "install", "--link-mode=copy", "-e", "."],
                capture_output=False,
            )

        log_info("✓ Build completed successfully")
        log_info("✓ 构建成功完成", lang="zh")
    except CommandError as e:
        log_error(f"Build failed: {e}")
        log_error(f"构建失败: {e}", lang="zh")
        raise
    except Exception as e:
        log_error(f"Unexpected error during build: {e}")
        log_error(f"构建过程中出现意外错误: {e}", lang="zh")
        raise CommandError(f"Build failed: {e}")


def build_project() -> None:
    """
    Build the project based on the current platform.

    Raises:
        CommandError: If the build fails.
    """
    # Determine if we're on Windows or Unix-like system
    if sys.platform.startswith("win"):
        build_windows()
    else:
        build_unix()
