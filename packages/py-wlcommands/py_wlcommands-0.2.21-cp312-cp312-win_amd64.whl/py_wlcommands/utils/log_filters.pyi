from _typeshed import Incomplete
from typing import Any

class LogFilter:
    context: Incomplete
    def __init__(self, **context) -> None: ...
    def filter(self, record: dict[str, Any]) -> bool: ...
