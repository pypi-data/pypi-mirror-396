from ...utils.project_root import find_project_root as find_project_root
from ...utils.workspace_detector import WorkspaceDetector as WorkspaceDetector
from _typeshed import Incomplete

class PythonEnvDetector:
    detector: Incomplete
    def __init__(self) -> None: ...
    def get_python_executable(self) -> str: ...
