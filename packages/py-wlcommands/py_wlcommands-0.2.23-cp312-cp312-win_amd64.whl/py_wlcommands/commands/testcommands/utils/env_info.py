from __future__ import annotations

import platform
import sys
from datetime import datetime
from typing import Any

# Try to import pytest for version information
_pytest: Any | None

try:
    import pytest  # type: ignore

    _pytest = pytest
except ImportError:
    _pytest = None


def get_env_info() -> list[str]:
    """获取测试环境信息。"""
    now = datetime.now().isoformat(timespec="seconds")
    py_ver = sys.version.replace("\n", " ")
    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"

    # Get pytest version if available
    if _pytest is not None:
        pytest_ver = getattr(_pytest, "__version__", "unknown")
    else:
        pytest_ver = "unknown"

    return [
        f"时间: {now}",
        f"Python: {py_ver}",
        f"OS: {os_info}",
        f"pytest: {pytest_ver}",
    ]
