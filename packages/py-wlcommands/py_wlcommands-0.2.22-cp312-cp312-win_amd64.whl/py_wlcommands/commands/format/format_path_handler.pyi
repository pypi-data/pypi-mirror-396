from ...utils.logging import log_info as log_info
from .python_formatter import format_with_python_tools as format_with_python_tools
from .rust_formatter import format_rust_code as format_rust_code
from pathlib import Path

class FormatPathHandler:
    def format_specified_paths(self, paths, env, quiet, unsafe: bool = False) -> None: ...
    def format_defaults(self, current_path: Path, env: dict, quiet: bool, unsafe: bool, for_lint: bool) -> None: ...
