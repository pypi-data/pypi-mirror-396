from _typeshed import Incomplete
from datetime import datetime as datetime, timedelta as timedelta

class LogRotator:
    filename: Incomplete
    max_size: Incomplete
    max_backups: Incomplete
    rotate_days: Incomplete
    def __init__(self, filename: str, max_size: int = ..., max_backups: int = 5, rotate_days: int = 7) -> None: ...
    def should_rotate(self) -> bool: ...
    def do_rotate(self) -> None: ...
