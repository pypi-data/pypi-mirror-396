"""Oomol Connect SDK for Python

这是 Oomol Connect 的 Python SDK，提供了与 Oomol Connect API 交互的完整功能。

主要功能：
- 任务管理（创建、运行、监控）
- 流程和区块查询
- 包管理（安装、查询）
- 智能轮询和进度监控

示例:
    >>> from oomol_connect_sdk import OomolConnectClient
    >>>
    >>> async with OomolConnectClient(
    ...     base_url="https://api.example.com/api",
    ...     api_token="your-token"
    ... ) as client:
    ...     # 运行任务
    ...     result = await client.tasks.run({
    ...         "blockId": "audio-lab::text-to-audio",
    ...         "inputValues": {"text": "你好"}
    ...     })
    ...     print(result["result"])
"""

from .blocks import BlocksClient
from .client import OomolConnectClient
from .errors import (
    ApiError,
    InstallFailedError,
    OomolConnectError,
    TaskFailedError,
    TaskStoppedError,
    TimeoutError,
)
from .packages import PackagesClient
from .tasks import TasksClient
from .types import (
    BackoffStrategy,
    Block,
    ClientOptions,
    CreateTaskRequest,
    InputHandle,
    InputValue,
    InstallTask,
    InstallTaskStatus,
    ListBlocksResponse,
    ListInstallTasksResponse,
    ListPackagesResponse,
    ListTasksResponse,
    NodeInputs,
    Package,
    PackageDependency,
    PollingOptions,
    RunResult,
    Task,
    TaskInputValues,
    TaskLog,
    TaskStatus,
)

__version__ = "1.0.2"

__all__ = [
    # 主客户端
    "OomolConnectClient",
    # 子客户端
    "BlocksClient",
    "TasksClient",
    "PackagesClient",
    # 错误类
    "OomolConnectError",
    "ApiError",
    "TaskFailedError",
    "TaskStoppedError",
    "TimeoutError",
    "InstallFailedError",
    # 类型
    "TaskStatus",
    "InputHandle",
    "InputValue",
    "NodeInputs",
    "TaskInputValues",
    "Task",
    "CreateTaskRequest",
    "TaskLog",
    "ListTasksResponse",
    "Block",
    "ListBlocksResponse",
    "InstallTaskStatus",
    "PackageDependency",
    "Package",
    "InstallTask",
    "ListPackagesResponse",
    "ListInstallTasksResponse",
    "BackoffStrategy",
    "PollingOptions",
    "ClientOptions",
    "RunResult",
]
