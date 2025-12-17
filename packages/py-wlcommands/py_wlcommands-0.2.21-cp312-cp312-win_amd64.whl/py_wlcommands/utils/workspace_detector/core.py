from pathlib import Path

from ..subprocess_utils import SubprocessExecutor
from .detection_strategies import (
    check_init_workspace,
    check_pyproject_workspace,
    check_tree_workspace,
    check_uv_lock_workspace,
)
from .types import ValidationResult, WorkspaceDetectionRules
from .venv_resolver import get_active_venv_path_str, get_venv_path


class WorkspaceDetector:
    def __init__(self, rules: WorkspaceDetectionRules | None = None) -> None:
        self._executor = SubprocessExecutor()
        self._cache: dict[str, bool] = {}
        self._rules: WorkspaceDetectionRules = {
            "use_pyproject": True,
            "use_uv_lock": True,
            "use_uv_init": True,
            "use_uv_tree": True,
            "uv_tree_min_roots": 2,
        }
        if rules:
            self._rules.update(rules)

    def detect(self, project_root: Path | None = None) -> bool:
        start = (project_root or Path(self._rules.get("cwd", "."))).resolve()
        key = str(start)
        if key in self._cache:
            return self._cache[key]

        try:
            root = self._find_workspace_root(start)

            if self._rules.get("use_pyproject", True) and check_pyproject_workspace(
                root
            ):
                self._cache[key] = True
                return True

            if self._rules.get("use_uv_lock", True) and check_uv_lock_workspace(root):
                self._cache[key] = True
                return True

            if self._rules.get("use_uv_init", True) and check_init_workspace(
                root, self._executor
            ):
                self._cache[key] = True
                return True

            min_roots = int(self._rules.get("uv_tree_min_roots", 2))
            if self._rules.get("use_uv_tree", True) and check_tree_workspace(
                root, self._executor, min_roots
            ):
                self._cache[key] = True
                return True

            self._cache[key] = False
            return False
        except Exception:
            self._cache[key] = False
            return False

    def validate(self, project_root: Path | None = None) -> ValidationResult:
        root = self._find_workspace_root(
            (project_root or Path(self._rules.get("cwd", "."))).resolve()
        )
        detected = self.detect(root)
        details: dict[str, str] = {}
        pyproject_path = root / "pyproject.toml"
        uv_lock_path = root / "uv.lock"
        details["pyproject.exists"] = str(pyproject_path.exists())
        details["uv.lock.exists"] = str(uv_lock_path.exists())
        details["apps.exists"] = str((root / "apps").exists())
        details["packages.exists"] = str((root / "packages").exists())
        return ValidationResult(valid=detected, details=details)

    def get_config(self) -> WorkspaceDetectionRules:
        return self._rules.copy()

    def resolve_path(self, path: str | Path, project_root: Path | None = None) -> Path:
        root = self._find_workspace_root(
            (project_root or Path(self._rules.get("cwd", "."))).resolve()
        )
        p = Path(path)
        if p.is_absolute():
            return p
        resolved = (root / p).resolve()
        return resolved

    def get_venv_path(self, project_root: Path | None = None) -> Path | None:
        root = self._find_workspace_root(
            (project_root or Path(self._rules.get("cwd", "."))).resolve()
        )
        return get_venv_path(root, self._executor)

    def get_active_venv_path_str(self, project_root: Path | None = None) -> str:
        root = self._find_workspace_root(
            (project_root or Path(self._rules.get("cwd", "."))).resolve()
        )
        return get_active_venv_path_str(root)

    def getActiveVenvPath(self, project_root: Path | None = None) -> str:  # noqa: N802
        """
        Alias for get_active_venv_path_str to support backward compatibility.

        This method uses camelCase naming for backward compatibility.
        """
        return self.get_active_venv_path_str(project_root)

    def _find_workspace_root(self, start: Path) -> Path:
        cur = start
        try:
            while True:
                if self._rules.get("use_pyproject", True) and check_pyproject_workspace(
                    cur
                ):
                    return cur
                if self._rules.get("use_uv_lock", True) and check_uv_lock_workspace(
                    cur
                ):
                    return cur
                if cur.parent == cur:
                    return start
                cur = cur.parent
        except Exception:
            return start

    def getConfig(self) -> WorkspaceDetectionRules:  # noqa: N802
        """
        Alias for get_config to support backward compatibility.

        This method uses camelCase naming for backward compatibility.
        """
        return self.get_config()

    def resolvePath(self, path: str | Path, project_root: Path | None = None) -> Path:  # noqa: N802
        """
        Alias for resolve_path to support backward compatibility.

        This method uses camelCase naming for backward compatibility.
        """
        return self.resolve_path(path, project_root)

    def getVenvPath(self, project_root: Path | None = None) -> Path | None:  # noqa: N802
        """
        Alias for get_venv_path to support backward compatibility.

        This method uses camelCase naming for backward compatibility.
        """
        return self.get_venv_path(project_root)
