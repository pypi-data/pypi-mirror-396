import os
from pathlib import Path

from ..logging import log_error, log_info
from ..subprocess_utils import SubprocessExecutor
from .exceptions import WorkspaceDetectionError


def get_venv_path(root: Path, executor: SubprocessExecutor) -> Path | None:
    """获取虚拟环境路径。"""
    env_path = os.environ.get("VENV_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p.resolve()
    local = root / ".venv"
    if local.exists():
        return local.resolve()
    try:
        res = executor.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                "import sys;print(sys.executable)",
            ],
            cwd=root,
            quiet=True,
        )
        if res.success and res.stdout:
            exe = Path(res.stdout.strip())
            parent = exe.parent
            venv_dir = parent.parent
            if venv_dir.exists():
                return venv_dir.resolve()
    except Exception:
        return None
    return None


def get_active_venv_path_str(root: Path) -> str:
    """获取当前激活的虚拟环境路径。"""
    log_info(f"Workspace venv path resolution at: {root}")

    # 检查工作区配置
    py = root / "pyproject.toml"
    uv_toml = root / "uv.toml"
    ws_json = root / "workspace.json"
    has_ws_conf = False
    try:
        if py.exists() and "tool.uv.workspace" in py.read_text(encoding="utf-8"):
            has_ws_conf = True
        if uv_toml.exists() or ws_json.exists():
            has_ws_conf = True
    except Exception:
        pass
    if not has_ws_conf:
        log_error("Workspace configuration file not found or invalid")
        raise WorkspaceDetectionError("Workspace configuration not found or invalid")

    # 检查虚拟环境是否激活
    venv_env = os.environ.get("VIRTUAL_ENV", "").strip()
    if not venv_env:
        log_error("Virtual environment is not activated (VIRTUAL_ENV not set)")
        raise WorkspaceDetectionError("Virtual environment not activated")

    venv_path = Path(venv_env)
    if not venv_path.exists():
        log_error(f"Activated virtual environment path does not exist: {venv_env}")
        raise WorkspaceDetectionError(
            "Activated virtual environment path does not exist"
        )

    resolved = venv_path.resolve()
    # Use platform-appropriate path separators instead of forcing POSIX format
    normalized = str(resolved)
    log_info(f"Resolved virtual environment path: {normalized}")
    return normalized


def get_active_venv_path(root: Path) -> str:
    """get_active_venv_path_str的别名，用于向后兼容。"""
    return get_active_venv_path_str(root)
