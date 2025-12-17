"""Build dist command for WL Commands."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from ...exceptions import CommandError
from ...utils.logging import log_error, log_info
from ...utils.uv_workspace import is_uv_workspace
from ...utils.workspace_detector import WorkspaceDetectionError, WorkspaceDetector
from .. import Command, register_command
from ..format.python_formatter import generate_type_stubs


@register_command("build dist")
class BuildDistCommand(Command):
    """Command to build distribution packages."""

    @property
    def name(self) -> str:
        """Return the command name."""
        return "dist"

    @property
    def help(self) -> str:
        """Return the command help text."""
        return "Build distribution packages"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--ws-min-roots",
            type=int,
            default=2,
            help="Minimum root packages to consider workspace (uv tree)",
        )
        parser.add_argument(
            "--ws-disable-tree", action="store_true", help="Disable uv tree detection"
        )
        parser.add_argument(
            "--ws-disable-init", action="store_true", help="Disable uv init detection"
        )
        parser.add_argument(
            "--ws-disable-pyproject",
            action="store_true",
            help="Disable pyproject workspace detection",
        )
        parser.add_argument(
            "--ws-disable-uv-lock",
            action="store_true",
            help="Disable uv.lock detection",
        )
        parser.add_argument(
            "--ws-strict",
            action="store_true",
            help="Fail build on abnormal workspace structure",
        )

    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Execute the build dist command."""
        # Determine the platform and run the appropriate build command
        try:
            log_info("Building distribution packages...")
            detector = WorkspaceDetector(self._build_rules(kwargs))  # type: ignore[arg-type]
            is_workspace = detector.detect(Path.cwd())
            self._validate_workspace(detector, is_workspace, kwargs)
            python_executable = self._resolve_python_executable(detector, is_workspace)
            self._generate_type_stubs()
            self._run_maturin(python_executable)
            self._cleanup_stubs()
            if is_workspace and Path(".venv").exists():
                log_info("In uv workspace, removing .venv directory...")
                shutil.rmtree(".venv")
                log_info("✓ .venv directory removed")
            log_info("✓ Distribution packages built successfully")
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to build distribution packages: {e}")
            raise CommandError(f"Build dist failed with return code {e.returncode}")
        except FileNotFoundError:
            log_error(
                "Maturin command not found. Please ensure maturin is installed and in PATH."
            )
            raise CommandError("Maturin command not found")
        except WorkspaceDetectionError as e:
            log_error(f"Workspace detection error: {e}")
            raise CommandError(f"Build dist failed: {e}")
        except Exception as e:
            log_error(f"Unexpected error during build dist: {e}")
            raise CommandError(f"Build dist failed: {e}")

    def _detect_uv_workspace(self) -> bool:
        """
        Detect if we are in a uv workspace.
        This is kept for backward compatibility with tests.

        Returns:
            bool: True if in a uv workspace, False otherwise.
        """
        return is_uv_workspace()

    def _create_venv(self) -> None:
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

    def _build_rules(self, kwargs: dict[str, object]) -> dict[str, object]:
        return {
            "uv_tree_min_roots": kwargs.get("ws_min_roots", 2),
            "use_uv_tree": not kwargs.get("ws_disable_tree", False),
            "use_uv_init": not kwargs.get("ws_disable_init", False),
            "use_pyproject": not kwargs.get("ws_disable_pyproject", False),
            "use_uv_lock": not kwargs.get("ws_disable_uv_lock", False),
        }

    def _validate_workspace(
        self, detector: WorkspaceDetector, is_workspace: bool, kwargs: dict[str, object]
    ) -> None:
        validation = detector.validate(Path.cwd())
        if not is_workspace and validation.details.get("pyproject.exists") == "True":
            msg = "Detected pyproject but workspace detection failed; check tool.uv.workspace"
            if kwargs.get("ws_strict", False):
                log_error(msg)
                raise CommandError(msg)
            else:
                log_info(f"Warning: {msg}")

    def _resolve_python_executable(
        self, detector: WorkspaceDetector, is_workspace: bool
    ) -> str | None:
        if not is_workspace:
            log_info("Not in uv workspace environment")
            return None
        log_info("✓ uv workspace environment detected")
        venv_root = detector.get_venv_path(Path.cwd())
        if venv_root is None:
            try:
                venv_str = detector.getActiveVenvPath(Path.cwd())
                venv_root = Path(venv_str)
            except Exception:
                venv_root = None
        if venv_root is None:
            log_info("No venv found, creating local .venv for build...")
            self._create_venv()
            venv_root = Path(".venv")
        if sys.platform.startswith("win"):
            return str((venv_root / "Scripts" / "python.exe").resolve())
        return str((venv_root / "bin" / "python").resolve())

    def _run_maturin(self, python_executable: str | None) -> None:
        command = ["maturin", "build", "--release", "--out", "dist"]
        if python_executable:
            command.extend(["-i", python_executable])
        log_info(f"Trying to build with: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=False, text=True)

    def _generate_type_stubs(self) -> None:
        root = Path.cwd()
        src_path = root / "src"
        typings_path = root / "typings"
        env = os.environ.copy()
        if not src_path.exists():
            log_error(f"Source directory not found for stubs: {src_path}")
            return
        log_info(f"Generating type stubs for {src_path} -> {typings_path}")
        try:
            generate_type_stubs(str(src_path), str(typings_path), env, quiet=False)
            log_info("✓ Type stubs generated")

            # Copy generated .pyi into package src so they are included in wheel
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
                # Fallback: copy all .pyi under typings preserving structure relative to src
                for pyi in typings_path.rglob("*.pyi"):
                    try:
                        # attempt to find 'py_wlcommands' segment
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

    def _cleanup_stubs(self) -> None:
        try:
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
