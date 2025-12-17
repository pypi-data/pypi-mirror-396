"""
Python environment detection utilities for test command.
"""

import os
import subprocess
import sys
from pathlib import Path

from ...utils.project_root import find_project_root
from ...utils.workspace_detector import WorkspaceDetector


class PythonEnvDetector:
    """Detect Python executable in different environments."""

    def __init__(self):
        """Initialize Python environment detector."""
        self.detector = WorkspaceDetector()

    def get_python_executable(self) -> str:
        """
        Get the Python executable path, using the same logic as wl build dist.

        Returns:
            str: Path to the Python executable
        """
        try:
            python_exe, _ = self._resolve_python()
            return python_exe or sys.executable
        except Exception:
            # 如果出现问题，回退到系统Python
            return sys.executable

    def _resolve_python(self) -> tuple[str | None, bool]:
        """
        Resolve Python executable path, with enhanced virtual environment detection.

        Returns:
            tuple: (python_path, is_virtual_env)
        """
        # 1. 检查是否在uv工作区环境中
        is_workspace = self.detector.detect(Path.cwd())
        print(f"Debug: uv workspace detected: {is_workspace}")

        # 如果不在工作区，直接返回python命令
        if not is_workspace:
            return "python", False

        # 2. 尝试通过不同方式查找虚拟环境中的Python
        python_path = self._find_python_in_uv_workspace()
        if python_path:
            return python_path, True

        python_path = self._find_python_in_custom_venv()
        if python_path:
            return python_path, True

        python_path = self._find_python_in_environment_venv()
        if python_path:
            return python_path, True

        # 3. 最后回退到系统Python
        print(f"Debug: Falling back to system Python: {sys.executable}")
        return sys.executable, False

    def _find_python_in_uv_workspace(self) -> str | None:
        """查找uv工作区中的Python可执行文件。"""
        venv_root = self.detector.get_venv_path(Path.cwd())
        if not venv_root:
            return None

        print(f"Debug: get_venv_path result: {venv_root}")

        # 尝试标准Python路径
        python_exe = self._get_python_path_from_venv(venv_root)
        if self._is_valid_python_executable(python_exe):
            return python_exe

        # 尝试python3路径
        if not sys.platform.startswith("win"):
            python_exe_alt = str((venv_root / "bin" / "python3").absolute())
            if self._is_valid_python_executable(python_exe_alt):
                return python_exe_alt

        # 尝试使用uv run
        return self._get_python_using_uv_run()

    def _find_python_in_custom_venv(self) -> str | None:
        """使用_find_venv方法查找Python。"""
        venv_path = self._find_venv()
        if not venv_path:
            return None

        venv_root = Path(venv_path)
        print(f"Debug: Found venv using _find_venv: {venv_root}")

        python_exe = self._get_python_path_from_venv(venv_root)
        if self._is_valid_python_executable(python_exe):
            return python_exe

        return None

    def _find_python_in_environment_venv(self) -> str | None:
        """通过VIRTUAL_ENV环境变量查找Python。"""
        virtual_env = os.environ.get("VIRTUAL_ENV")
        if not virtual_env:
            return None

        venv_root = Path(virtual_env)
        print(f"Debug: Using VIRTUAL_ENV: {venv_root}")

        python_exe = self._get_python_path_from_venv(venv_root)
        if self._is_valid_python_executable(python_exe):
            return python_exe

        return None

    def _get_python_path_from_venv(self, venv_root: Path) -> str:
        """从虚拟环境根目录构造Python可执行文件路径。"""
        if sys.platform.startswith("win"):
            return str((venv_root / "Scripts" / "python.exe").absolute())
        else:
            return str((venv_root / "bin" / "python").absolute())

    def _is_valid_python_executable(self, python_path: str) -> bool:
        """检查Python可执行文件是否存在。"""
        print(f"Debug: Checking Python executable at: {python_path}")
        if Path(python_path).exists():
            print(f"Debug: Successfully found Python executable: {python_path}")
            return True
        print(f"Debug: Python executable does not exist at: {python_path}")
        return False

    def _get_python_using_uv_run(self) -> str | None:
        """使用uv run获取Python可执行文件路径。"""
        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-c",
                    "import sys; print(sys.executable)",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            uv_python = result.stdout.strip()
            print(f"Debug: Using uv run python result: {uv_python}")
            if Path(uv_python).exists():
                return uv_python
        except Exception as e:
            print(f"Debug: uv run python failed: {e}")
        return None

    def _find_venv(self) -> str | None:
        """
        Find virtual environment path if it exists.

        Returns:
            str | None: Path to virtual environment or None if not found
        """

        project_root = self._get_project_root()

        # Check common virtual environment locations
        possible_venv_paths = [
            os.path.join(project_root, ".venv"),
            os.path.join(project_root, "venv"),
        ]

        for venv_path in possible_venv_paths:
            if os.path.exists(os.path.join(venv_path, "pyvenv.cfg")):
                return venv_path

        return None

    def _get_project_root(self) -> str:
        """
        Get the project root directory.

        Returns:
            str: Path to the project root directory
        """
        try:
            cwd = Path.cwd()
            if (cwd / "tests").exists() or (cwd / "src").exists():
                return str(cwd)
            root = find_project_root()
            return str(root)
        except Exception:
            return os.getcwd()
