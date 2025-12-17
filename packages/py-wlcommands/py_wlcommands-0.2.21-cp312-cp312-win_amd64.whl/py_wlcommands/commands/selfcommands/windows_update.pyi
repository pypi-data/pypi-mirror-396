from ..self import subprocess as subprocess, sys as sys

class WindowsUpdate:
    def handle_access_error(self, uv_path: str = None) -> None: ...
