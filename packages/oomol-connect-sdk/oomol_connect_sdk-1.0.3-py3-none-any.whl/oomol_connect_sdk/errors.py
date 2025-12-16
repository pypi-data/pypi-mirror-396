"""Custom error classes"""

from typing import Any, Optional


class OomolConnectError(Exception):
    """Base class for all Oomol Connect SDK errors"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ApiError(OomolConnectError):
    """HTTP API error"""

    def __init__(self, message: str, status: int, response: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.response = response

    def __str__(self) -> str:
        return f"ApiError({self.status}): {self.message}"


class TaskFailedError(OomolConnectError):
    """Task execution failed error"""

    def __init__(self, message: str, task_id: str, task: Optional[Any] = None) -> None:
        super().__init__(message)
        self.task_id = task_id
        self.task = task

    def __str__(self) -> str:
        return f"TaskFailedError: Task {self.task_id} failed - {self.message}"


class TaskStoppedError(OomolConnectError):
    """Task was stopped error"""

    def __init__(self, message: str, task_id: str, task: Optional[Any] = None) -> None:
        super().__init__(message)
        self.task_id = task_id
        self.task = task

    def __str__(self) -> str:
        return f"TaskStoppedError: Task {self.task_id} was stopped - {self.message}"


class TimeoutError(OomolConnectError):
    """Polling timeout error"""

    def __init__(self, message: str) -> None:
        super().__init__(message)

    def __str__(self) -> str:
        return f"TimeoutError: {self.message}"


class InstallFailedError(OomolConnectError):
    """Package installation failed error"""

    def __init__(self, message: str, task_id: str, task: Optional[Any] = None) -> None:
        super().__init__(message)
        self.task_id = task_id
        self.task = task

    def __str__(self) -> str:
        return f"InstallFailedError: Install task {self.task_id} failed - {self.message}"
