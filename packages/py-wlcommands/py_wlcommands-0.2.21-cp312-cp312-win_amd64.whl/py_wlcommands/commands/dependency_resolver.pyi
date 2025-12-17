from ..infrastructure.dependency_injection import resolve as resolve
from typing import Any

def resolve_dependencies(**annotations: Any) -> dict[str, Any]: ...
