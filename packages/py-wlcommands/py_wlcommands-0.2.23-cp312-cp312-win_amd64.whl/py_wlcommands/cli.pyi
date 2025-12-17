from . import __version__ as __version__
from .utils.error_handler import ErrorHandler as ErrorHandler
from .utils.logging import log_error as log_error
from _typeshed import Incomplete

logger: Incomplete

def main(argv: list[str] | None = None) -> int: ...
