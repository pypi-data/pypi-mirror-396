from ..self import subprocess as subprocess, sys as sys

class PypiUpdater:
    def update(self, uv_path: str, env: dict) -> None: ...
