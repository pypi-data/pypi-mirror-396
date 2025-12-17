from __future__ import annotations

from pathlib import Path
from typing import Any


def fmt_pct(x: Any) -> str:
    """格式化百分比值。"""
    try:
        v = float(x)
        return f"{v:.2f}%"
    except Exception:
        return "N/A"


def write_md(path: str, lines: list[str]) -> None:
    """将文本行写入Markdown文件。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
