from ...utils.logging import log_info as log_info
from ...utils.subprocess_utils import SubprocessExecutor as SubprocessExecutor, SubprocessResult as SubprocessResult
from pathlib import Path

class LintReporter:
    def generate_report(self, result: SubprocessResult, project_root: Path, quiet: bool, paths: list[str] | None, fix: bool) -> None: ...
