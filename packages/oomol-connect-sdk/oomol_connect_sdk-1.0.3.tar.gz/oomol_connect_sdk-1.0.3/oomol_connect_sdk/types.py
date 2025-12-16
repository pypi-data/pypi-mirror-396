"""Type definitions"""

from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict, Union


# ============ Common Types ============

TaskStatus = Literal["created", "pending", "running", "completed", "failed", "stopped"]


class InputHandle(TypedDict, total=False):
    """Input handle"""
    handle: str
    json_schema: Optional[Dict[str, Any]]


class InputValue(TypedDict):
    """Input value"""
    handle: str
    value: Any


class NodeInputs(TypedDict):
    """Node inputs"""
    nodeId: str
    inputs: List[InputValue]


# Three formats of input values
TaskInputValues = Union[
    Dict[str, Any],  # Format 1: Simple object format
    List[InputValue],  # Format 2: Array format
    List[NodeInputs]  # Format 3: Node format (multi-node)
]


# ============ Task Related Types ============

class Task(TypedDict, total=False):
    """Task"""
    id: str
    status: TaskStatus
    project_id: str
    manifest_path: str
    inputValues: Optional[List[NodeInputs]]
    created_at: int  # Unix timestamp (milliseconds)
    updated_at: int


class CreateTaskRequest(TypedDict, total=False):
    """Create task request"""
    blockId: str
    inputValues: Optional[TaskInputValues]


class TaskLog(TypedDict, total=False):
    """Task log"""
    id: int
    project_name: str
    session_id: str
    node_id: str
    manifest_path: str
    type: str
    event: Optional[Dict[str, Any]]
    created_at: int


class ListTasksResponse(TypedDict):
    """List tasks response"""
    tasks: List[Task]


# ============ Block Related Types ============

class Block(TypedDict, total=False):
    """Block"""
    package: str
    name: str
    path: str
    description: Optional[str]
    inputs: Optional[List[InputHandle]]
    blockId: str  # Auto-generated block ID (format: package::name)
    version: str  # Version number extracted from path


class ListBlocksResponse(TypedDict):
    """List blocks response"""
    blocks: List[Block]


# ============ Package Related Types ============

InstallTaskStatus = Literal["pending", "running", "success", "failed"]


class PackageDependency(TypedDict, total=False):
    """Package dependency"""
    name: str
    version: Optional[str]


class Package(TypedDict, total=False):
    """Package"""
    name: str
    version: str
    path: str
    description: Optional[str]


class InstallTask(TypedDict, total=False):
    """Installation task"""
    id: str
    name: str
    version: Optional[str]
    status: InstallTaskStatus
    packagePath: Optional[str]
    dependencies: Optional[List[PackageDependency]]
    error: Optional[str]
    createdAt: int
    updatedAt: int


class ListPackagesResponse(TypedDict):
    """List packages response"""
    packages: List[Package]


class ListInstallTasksResponse(TypedDict):
    """List installation tasks response"""
    tasks: List[InstallTask]


# ============ Configuration Types ============

class BackoffStrategy(str, Enum):
    """Backoff strategy"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"


class PollingOptions(TypedDict, total=False):
    """Polling options"""
    interval_ms: int  # Polling interval, default 2000ms
    timeout_ms: Optional[int]  # Timeout duration, default unlimited
    max_interval_ms: int  # Maximum interval, default 10000ms
    backoff_strategy: BackoffStrategy  # Backoff strategy
    backoff_factor: float  # Backoff factor, default 1.5
    on_progress: Optional[Callable[[Task], None]]  # Progress callback
    on_log: Optional[Callable[[TaskLog], None]]  # Log callback


class ClientOptions(TypedDict, total=False):
    """Client configuration"""
    base_url: str  # Base URL, default "/api"
    api_token: Optional[str]  # API Token (automatically added as Bearer token)
    default_headers: Optional[Dict[str, str]]  # Default request headers
    timeout: Optional[float]  # Request timeout (seconds)


# ============ Run Task Result Types ============

class RunResult(TypedDict, total=False):
    """Run task result"""
    task_id: str
    task: Task
    logs: List[TaskLog]
    result: Optional[Any]  # Result automatically extracted from logs


# ============ Applet Related Types ============

class AppletData(TypedDict, total=False):
    """Applet data"""
    id: str  # Required: applet data ID
    createdAt: int  # Required: creation timestamp
    packageId: str  # Required: associated package ID (format: "package-name-x.y.z")
    blockName: str  # Required: associated block name
    title: Optional[str]  # Optional: applet title
    description: Optional[str]  # Optional: applet description
    presetInputs: Optional[Dict[str, Any]]  # Optional: preset input parameters


class Applet(TypedDict, total=False):
    """Applet"""
    appletId: str  # Required: applet unique ID
    userId: str  # Required: creator user ID
    data: AppletData  # Required: applet data
    createdAt: int  # Required: creation timestamp
    updatedAt: int  # Required: update timestamp


class RunAppletRequest(TypedDict, total=False):
    """Run Applet request"""
    applet_id: str  # Required: applet ID to run
    input_values: Optional[TaskInputValues]  # Optional: user input parameters (will override preset values)


ListAppletsResponse = List[Applet]  # List applets response
