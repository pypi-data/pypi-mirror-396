import subprocess
from ..exceptions import CommandError as CommandError

def run_command(command, env=None, capture_output: bool = False, text: bool = True) -> subprocess.CompletedProcess: ...
