class WorkspaceDetectionError(Exception):
    """工作区检测错误异常。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
