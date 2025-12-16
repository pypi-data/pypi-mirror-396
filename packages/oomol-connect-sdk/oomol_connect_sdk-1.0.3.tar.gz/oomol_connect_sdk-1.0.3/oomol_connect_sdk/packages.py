"""Packages client"""

import time
from typing import TYPE_CHECKING, Optional

from .errors import InstallFailedError, TimeoutError
from .types import (
    BackoffStrategy,
    InstallTask,
    ListInstallTasksResponse,
    ListPackagesResponse,
    PollingOptions,
)
from .utils import sleep

if TYPE_CHECKING:
    from .client import OomolConnectClient


class PackagesClient:
    """Packages API client

    Used to manage package installation and queries.
    """

    def __init__(self, client: "OomolConnectClient") -> None:
        """Initialize Packages client

        Args:
            client: Main client instance
        """
        self._client = client

    async def list(self) -> ListPackagesResponse:
        """List installed packages

        Returns:
            Response containing package list

        Example:
            >>> packages_response = await client.packages.list()
            >>> for pkg in packages_response["packages"]:
            ...     print(pkg["name"], pkg["version"])
        """
        return await self._client.request("/packages", method="GET")

    async def install(
        self,
        name: str,
        version: Optional[str] = None,
    ) -> InstallTask:
        """Install package

        Args:
            name: Package name
            version: Version (optional)

        Returns:
            Installation task information

        Example:
            >>> install_task = await client.packages.install("audio-lab", "1.0.0")
            >>> print(install_task["id"], install_task["status"])
        """
        data = {"name": name}
        if version:
            data["version"] = version

        return await self._client.request(
            "/packages/install",
            method="POST",
            json_data=data
        )

    async def list_install_tasks(self) -> ListInstallTasksResponse:
        """List installation tasks

        Returns:
            Response containing installation task list

        Example:
            >>> tasks_response = await client.packages.list_install_tasks()
            >>> for task in tasks_response["tasks"]:
            ...     print(task["name"], task["status"])
        """
        return await self._client.request("/packages/install", method="GET")

    async def get_install_task(self, task_id: str) -> InstallTask:
        """Get installation task details

        Args:
            task_id: Installation task ID

        Returns:
            Installation task details

        Example:
            >>> task = await client.packages.get_install_task("task-123")
            >>> print(task["status"])
        """
        return await self._client.request(
            f"/packages/install/{task_id}",
            method="GET"
        )

    async def wait_for_install_completion(
        self,
        task_id: str,
        options: Optional[PollingOptions] = None,
    ) -> InstallTask:
        """Poll and wait for installation completion

        Args:
            task_id: Installation task ID
            options: Polling configuration options

        Returns:
            Completed installation task information

        Raises:
            InstallFailedError: Installation failed
            TimeoutError: Polling timeout

        Example:
            >>> task = await client.packages.wait_for_install_completion(
            ...     "task-123",
            ...     {"interval_ms": 1000, "timeout_ms": 60000}
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

        start_time = time.time() * 1000  # Convert to milliseconds
        current_interval = interval_ms
        attempt = 0

        while True:
            # Check timeout
            if timeout_ms:
                elapsed = time.time() * 1000 - start_time
                if elapsed >= timeout_ms:
                    raise TimeoutError(
                        f"Install task {task_id} did not complete within {timeout_ms}ms"
                    )

            # Get installation task status
            task = await self.get_install_task(task_id)

            # Progress callback
            if on_progress:
                on_progress(task)  # type: ignore

            # Check status
            status = task["status"]
            if status == "success":
                return task
            elif status == "failed":
                error = task.get("error", "Unknown error")
                raise InstallFailedError(
                    f"Install task {task_id} failed: {error}",
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

    async def install_and_wait(
        self,
        name: str,
        version: Optional[str] = None,
        polling_options: Optional[PollingOptions] = None,
    ) -> InstallTask:
        """Install package and wait for completion

        Convenience method that combines install() and wait_for_install_completion().

        Args:
            name: Package name
            version: Version (optional)
            polling_options: Polling configuration options

        Returns:
            Completed installation task information

        Example:
            >>> task = await client.packages.install_and_wait("audio-lab", "1.0.0")
            >>> print(task["packagePath"])
        """
        install_task = await self.install(name, version)
        task_id = install_task["id"]
        return await self.wait_for_install_completion(task_id, polling_options)
