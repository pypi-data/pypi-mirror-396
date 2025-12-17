from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: str) -> dict[str, Any]:
    """读取JSON文件并返回其内容。"""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def coverage_totals(
    data: dict[str, Any],
) -> tuple[float | None, float | None, int, int, int]:
    """计算覆盖率统计信息。"""
    files = data.get("files", {})
    num_files = len(files) if isinstance(files, dict) else 0
    covered_lines = 0
    total_lines = 0
    covered_branches = 0
    total_branches = 0
    if isinstance(files, dict):
        for info in files.values():
            s = info.get("summary", {})
            try:
                covered_lines += int(s.get("covered_lines", 0))
                total_lines += int(s.get("num_statements", s.get("num_lines", 0)))
                covered_branches += int(s.get("covered_branches", 0))
                total_branches += int(s.get("num_branches", 0))
            except Exception:
                pass
    line_pct = (covered_lines / total_lines * 100.0) if total_lines else None
    branch_pct = (covered_branches / total_branches * 100.0) if total_branches else None
    return (
        line_pct,
        branch_pct,
        total_lines,
        total_branches,
        num_files,
    )


def file_entries(
    data: dict[str, Any], project_root: str
) -> list[tuple[str, float | None, float | None]]:
    """获取文件覆盖率条目列表。"""
    files = data.get("files", {})
    res: list[tuple[str, float | None, float | None]] = []
    if isinstance(files, dict):
        for path, info in files.items():
            rel = path
            try:
                rel = str(
                    Path(path).resolve().relative_to(Path(project_root).resolve())
                )
            except Exception:
                pass
            s = info.get("summary", {})

            # Get line coverage percentage
            lp = s.get("percent_covered")
            if lp is None:
                lp = info.get("percent_covered")
            # If still None, calculate from covered_lines and num_statements
            if lp is None:
                covered_lines = s.get("covered_lines", 0)
                num_statements = s.get("num_statements", s.get("num_lines", 0))
                if num_statements > 0:
                    lp = (covered_lines / num_statements) * 100

            # Get branch coverage percentage
            bp = s.get("percent_branches")
            if bp is None:
                bp = info.get("percent_branches")
            # If still None, calculate from covered_branches and num_branches
            if bp is None:
                covered_branches = s.get("covered_branches", 0)
                num_branches = s.get("num_branches", 0)
                if num_branches > 0:
                    bp = (covered_branches / num_branches) * 100

            try:
                lp_f = float(lp) if lp is not None else None
            except Exception:
                lp_f = None
            try:
                bp_f = float(bp) if bp is not None else None
            except Exception:
                bp_f = None
            res.append((rel, lp_f, bp_f))
    return res
