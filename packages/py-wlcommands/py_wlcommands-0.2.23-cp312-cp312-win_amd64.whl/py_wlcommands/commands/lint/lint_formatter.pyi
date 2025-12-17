from ...utils.logging import log_info as log_info
from ..format import FormatCommand as FormatCommand
from pathlib import Path

class LintFormatter:
    def format_code(self, project_root: Path, paths: list[str] | None, quiet: bool) -> None: ...
