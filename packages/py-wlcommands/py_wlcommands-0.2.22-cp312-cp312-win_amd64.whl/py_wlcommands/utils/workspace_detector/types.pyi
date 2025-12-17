from dataclasses import dataclass
from typing import TypedDict

class WorkspaceDetectionRules(TypedDict, total=False):
    use_pyproject: bool
    use_uv_lock: bool
    use_uv_init: bool
    use_uv_tree: bool
    uv_tree_min_roots: int
    cwd: str

@dataclass
class ValidationResult:
    valid: bool
    details: dict[str, str]
