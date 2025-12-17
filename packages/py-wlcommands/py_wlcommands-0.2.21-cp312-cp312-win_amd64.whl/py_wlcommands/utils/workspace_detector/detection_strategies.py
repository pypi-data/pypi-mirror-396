from pathlib import Path

from ..subprocess_utils import SubprocessExecutor


def check_pyproject_workspace(root: Path) -> bool:
    """检查pyproject.toml中是否包含workspace配置。"""
    py = root / "pyproject.toml"
    if not py.exists():
        return False
    try:
        content = py.read_text(encoding="utf-8")
        return "[tool.uv.workspace]" in content or "tool.uv.workspace" in content
    except Exception:
        return False


def check_uv_lock_workspace(root: Path) -> bool:
    """检查uv.lock文件是否包含足够多的包。"""
    lock = root / "uv.lock"
    if not lock.exists():
        return False
    try:
        content = lock.read_text(encoding="utf-8")
        count = content.count("[package]")
        return count >= 5
    except Exception:
        return False


def check_init_workspace(root: Path, executor: SubprocessExecutor) -> bool:
    """使用uv init --dry-run检查是否已在工作区中。"""
    try:
        result = executor.run(
            ["uv", "init", "--dry-run"], cwd=root, quiet=True, cache_result=True
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.success and ("is already a member of workspace" in output)
    except Exception:
        return False


def check_tree_workspace(
    root: Path, executor: SubprocessExecutor, min_roots: int = 2
) -> bool:
    """使用uv tree检查根包数量是否达到最小值。"""
    try:
        result = executor.run(["uv", "tree"], cwd=root, quiet=True, cache_result=True)
        if not result.success or not result.stdout:
            return False
        lines = result.stdout.split("\n")
        roots = parse_root_packages(lines)
        return len(roots) >= min_roots
    except Exception:
        return False


def parse_root_packages(lines: list[str]) -> list[str]:
    """从uv tree输出中解析根包。"""
    roots: list[str] = []
    for line in lines:
        if (
            not line.startswith(" ")
            and line.strip()
            and not line.startswith("Resolved")
            and not line.startswith("(*)")
            and not line.startswith("v")  # 排除以v开头的版本号行
        ):
            if " v" in line:
                parts = line.split(" v", 1)
                if len(parts) == 2:
                    name = parts[0]
                    ver = parts[1]
                    if (
                        name
                        and not name.startswith(("├", "└", "│"))
                        and is_valid_version(ver)
                    ):
                        roots.append(name)
            elif line and not line.startswith(("├", "└", "│")):
                roots.append(line.strip())
    return roots


def is_valid_version(version: str) -> bool:
    """检查版本字符串是否有效。"""
    if not version:
        return False
    return all(c.isalnum() or c in ".-+" for c in version)
