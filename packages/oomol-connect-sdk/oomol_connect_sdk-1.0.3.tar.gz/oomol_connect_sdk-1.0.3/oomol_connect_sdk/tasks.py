"""Tasks client"""

import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .errors import TaskFailedError, TaskStoppedError, TimeoutError
from .types import (
    BackoffStrategy,
    CreateTaskRequest,
    ListTasksResponse,
    PollingOptions,
    RunResult,
    Task,
    TaskInputValues,
    TaskLog,
)
from .utils import extract_result_from_logs, normalize_input_values, sleep

if TYPE_CHECKING:
    from .client import OomolConnectClient


class TasksClient:
    """Tasks API client

    This is the core client of the SDK, providing task creation, management, and monitoring functionalities.
    """

    def __init__(self, client: "OomolConnectClient") -> None:
        """Initialize Tasks client

        Args:
            client: Main client instance
        """
        self._client = client

    async def list(self) -> ListTasksResponse:
        """List all tasks

        Returns:
            Response containing task list

        Example:
            >>> tasks_response = await client.tasks.list()
            >>> for task in tasks_response["tasks"]:
            ...     print(task["id"], task["status"])
        """
        return await self._client.request("/v1/tasks", method="GET")

    async def create(self, request: CreateTaskRequest) -> Dict[str, Any]:
        """Create task (JSON format)

        Args:
            request: Create task request

        Returns:
            Created task information

        Example:
            >>> task = await client.tasks.create({
            ...     "blockId": "audio-lab::text-to-audio",
            ...     "inputValues": {"text": "你好"}
            ... })
            >>> print(task["id"])
        """
        # Normalize input values
        request_data = dict(request)
        if "inputValues" in request_data and request_data["inputValues"]:
            request_data["inputValues"] = normalize_input_values(
                request_data["inputValues"]
            )

        return await self._client.request(
            "/v1/tasks",
            method="POST",
            json_data=request_data
        )

    async def create_with_files(
        self,
        block_id: str,
        input_values: Optional[TaskInputValues] = None,
        files: Optional[Union[Any, List[Any]]] = None,
    ) -> Dict[str, Any]:
        """Create task (with file upload support)

        Args:
            block_id: Block ID (format: package::name)
            input_values: Input values
            files: File or file list

        Returns:
            Created task information

        Example:
            >>> with open("test.txt", "rb") as f:
            ...     task = await client.tasks.create_with_files(
            ...         "pkg::block",
            ...         {"input1": "value"},
            ...         f
            ...     )
        """
        # Prepare form data
        data = {"blockId": block_id}

        # Normalize input values
        if input_values:
            import json
            normalized = normalize_input_values(input_values)
            data["inputValues"] = json.dumps(normalized)

        # Prepare file data
        files_data = None
        if files:
            if not isinstance(files, list):
                files = [files]
            files_data = [("files", f) for f in files]

        return await self._client.request(
            "/v1/tasks",
            method="POST",
            data=data,
            files=files_data
        )

    async def get(self, task_id: str) -> Task:
        """Get task details

        Args:
            task_id: Task ID

        Returns:
            Task details

        Example:
            >>> task = await client.tasks.get("task-123")
            >>> print(task["status"])
        """
        response = await self._client.request(f"/v1/tasks/{task_id}", method="GET")
        # API returns {"task": {...}, "success": true}, extract task field
        return response.get("task", response)

    async def stop(self, task_id: str) -> Task:
        """Stop task

        Args:
            task_id: Task ID

        Returns:
            Updated task information

        Example:
            >>> task = await client.tasks.stop("task-123")
            >>> print(task["status"])  # "stopped"
        """
        return await self._client.request(
            f"/v1/tasks/{task_id}/stop",
            method="POST"
        )

    async def get_logs(self, task_id: str) -> List[TaskLog]:
        """Get task logs

        Args:
            task_id: Task ID

        Returns:
            Task log list

        Example:
            >>> logs = await client.tasks.get_logs("task-123")
            >>> for log in logs:
            ...     print(log["type"], log.get("event"))
        """
        response = await self._client.request(
            f"/v1/tasks/{task_id}/logs",
            method="GET"
        )
        return response.get("logs", [])

    async def wait_for_completion(
        self,
        task_id: str,
        options: Optional[PollingOptions] = None,
    ) -> Task:
        """Poll and wait for task completion

        Uses smart polling strategy, supports progress callbacks and real-time log streaming.

        Args:
            task_id: Task ID
            options: Polling configuration options

        Returns:
            Completed task information

        Raises:
            TaskFailedError: Task execution failed
            TaskStoppedError: Task was stopped
            TimeoutError: Polling timeout

        Example:
            >>> task = await client.tasks.wait_for_completion(
            ...     "task-123",
            ...     {
            ...         "interval_ms": 2000,
            ...         "timeout_ms": 300000,
            ...         "on_progress": lambda t: print(t["status"]),
            ...         "on_log": lambda log: print(log["type"])
            ...     }
            ... )
        """
        options = options or {}

        # Default configuration
        interval_ms = options.get("interval_ms", 2000)
        timeout_ms = options.get("timeout_ms")
        max_interval_ms = options.get("max_interval_ms", 10000)
        backoff_strategy = options.get("backoff_strategy", BackoffStrategy.EXPONENTIAL)
        backoff_factor = options.get("backoff_factor", 1.5)
        on_progress = options.get("on_progress")
        on_log = options.get("on_log")

        start_time = time.time() * 1000  # Convert to milliseconds
        current_interval = interval_ms
        attempt = 0
        last_log_id = 0

        while True:
            # Check timeout
            if timeout_ms:
                elapsed = time.time() * 1000 - start_time
                if elapsed >= timeout_ms:
                    raise TimeoutError(
                        f"Task {task_id} did not complete within {timeout_ms}ms"
                    )

            # Get task status
            task = await self.get(task_id)

            # Progress callback
            if on_progress:
                on_progress(task)

            # Get new logs
            if on_log:
                all_logs = await self.get_logs(task_id)
                new_logs = [log for log in all_logs if log["id"] > last_log_id]
                for log in new_logs:
                    on_log(log)
                    last_log_id = log["id"]

            # Check task status
            status = task["status"]
            if status == "completed":
                return task
            elif status == "failed":
                raise TaskFailedError(
                    f"Task {task_id} failed",
                    task_id=task_id,
                    task=task
                )
            elif status == "stopped":
                raise TaskStoppedError(
                    f"Task {task_id} was stopped",
                    task_id=task_id,
                    task=task
                )

            # Calculate next polling interval (backoff algorithm)
            if backoff_strategy == BackoffStrategy.EXPONENTIAL:
                current_interval = min(
                    max_interval_ms,
                    interval_ms * (backoff_factor ** attempt)
                )
            else:
                current_interval = interval_ms

            # Wait
            await sleep(int(current_interval))
            attempt += 1

    async def create_and_wait(
        self,
        request: CreateTaskRequest,
        polling_options: Optional[PollingOptions] = None,
    ) -> Task:
        """Create task and wait for completion

        Convenience method that combines create() and wait_for_completion().

        Args:
            request: Create task request
            polling_options: Polling configuration options

        Returns:
            Completed task information

        Example:
            >>> task = await client.tasks.create_and_wait({
            ...     "blockId": "audio-lab::text-to-audio",
            ...     "inputValues": {"input1": "value"}
            ... })
        """
        response = await self.create(request)
        task_id = response["task"]["id"]
        return await self.wait_for_completion(task_id, polling_options)

    async def run(
        self,
        request: CreateTaskRequest,
        polling_options: Optional[PollingOptions] = None,
    ) -> RunResult:
        """Run task and get result (recommended method)

        Complete in one step: create → poll → get logs → extract result.

        Args:
            request: Create task request
            polling_options: Polling configuration options

        Returns:
            Run result containing task ID, task info, logs, and extracted result

        Example:
            >>> result = await client.tasks.run({
            ...     "blockId": "audio-lab::text-to-audio",
            ...     "inputValues": {"text": "你好"}
            ... })
            >>> print(result["task_id"])
            >>> print(result["result"])
        """
        # Create task
        response = await self.create(request)
        task_id = response["task"]["id"]

        # Wait for completion
        task = await self.wait_for_completion(task_id, polling_options)

        # Get logs
        logs = await self.get_logs(task_id)

        # Extract result
        result = extract_result_from_logs(logs)

        return RunResult(
            task_id=task_id,
            task=task,
            logs=logs,
            result=result
        )

    async def run_with_files(
        self,
        block_id: str,
        input_values: Optional[TaskInputValues] = None,
        files: Optional[Union[Any, List[Any]]] = None,
        polling_options: Optional[PollingOptions] = None,
    ) -> RunResult:
        """Run task (with file upload) and get result

        Complete file upload task in one step: create (with files) → poll → get logs → extract result.

        Args:
            block_id: Block ID (format: package::name)
            input_values: Input values
            files: File or file list
            polling_options: Polling configuration options

        Returns:
            Run result

        Example:
            >>> with open("test.txt", "rb") as f:
            ...     result = await client.tasks.run_with_files(
            ...         "pkg::block",
            ...         {"input1": "value"},
            ...         f
            ...     )
        """
        # Create task (with files)
        response = await self.create_with_files(block_id, input_values, files)
        task_id = response["task"]["id"]

        # Wait for completion
        task = await self.wait_for_completion(task_id, polling_options)

        # Get logs
        logs = await self.get_logs(task_id)

        # Extract result
        result = extract_result_from_logs(logs)

        return RunResult(
            task_id=task_id,
            task=task,
            logs=logs,
            result=result
        )
