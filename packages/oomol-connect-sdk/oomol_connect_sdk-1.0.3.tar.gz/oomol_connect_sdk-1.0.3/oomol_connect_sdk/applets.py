"""Applets client"""

import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .errors import ApiError
from .types import (
    Applet,
    ListAppletsResponse,
    PollingOptions,
    RunResult,
    TaskInputValues,
)
from .utils import normalize_input_values

if TYPE_CHECKING:
    from .client import OomolConnectClient


# Applets query server URL (built-in)
APPLETS_QUERY_SERVER = "https://chat-data.oomol.com"


class AppletsClient:
    """Applets API client

    Provides functionality to query and run Applets (blocks with preset parameters).

    Note: Applets queries use the built-in query server (https://chat-data.oomol.com),
    task execution uses the user-configured server.
    """

    def __init__(self, client: "OomolConnectClient") -> None:
        """Initialize Applets client

        Args:
            client: Main client instance
        """
        self._client = client

    async def list(self) -> ListAppletsResponse:
        """List all applets

        Uses the built-in query server to retrieve applets list.

        Returns:
            List of applets

        Example:
            >>> applets = await client.applets.list()
            >>> for applet in applets:
            ...     print(applet["applet_id"], applet["data"]["title"])
        """
        # Use built-in query server
        response = await self._client.request_to_server(
            server_url=APPLETS_QUERY_SERVER,
            path="/rpc/listApplets",
            method="POST",
            json_data={}
        )
        return response

    async def run(
        self,
        applet_id: str,
        input_values: Optional[TaskInputValues] = None,
        polling_options: Optional[PollingOptions] = None,
    ) -> RunResult:
        """Run an applet (block with preset parameters)

        1. Find the applet
        2. Merge preset parameters and user parameters (user parameters take priority)
        3. Construct blockId
        4. Call tasks.run() to execute the task

        Args:
            applet_id: Applet ID to run
            input_values: User input parameters (will override preset values)
            polling_options: Polling configuration options

        Returns:
            Run result containing task ID, task info, logs, and extracted result

        Raises:
            ApiError: Throws 404 error when applet does not exist

        Example:
            >>> # Use all preset parameters
            >>> result = await client.applets.run(
            ...     applet_id="84dc8cac-7f91-4bd1-a3b6-6715bf4f81c9"
            ... )
            >>> print(result["result"])
            >>>
            >>> # Override some parameters
            >>> result = await client.applets.run(
            ...     applet_id="84dc8cac-7f91-4bd1-a3b6-6715bf4f81c9",
            ...     input_values={"content": "test", "indent": 4}
            ... )
        """
        # 1. Find applet
        applets = await self.list()
        applet = next((a for a in applets if a["appletId"] == applet_id), None)

        if not applet:
            raise ApiError(
                message=f"Applet not found: {applet_id}",
                status=404,
                response=None
            )

        # 2. Merge parameters
        preset_inputs = applet["data"].get("presetInputs")
        merged_inputs = self._merge_input_values(preset_inputs, input_values)

        # 3. Construct blockId
        package_name = self._extract_package_name(applet["data"]["packageId"])
        block_id = f"{package_name}::{applet['data']['blockName']}"

        # 4. Call tasks.run()
        return await self._client.tasks.run(
            request={
                "blockId": block_id,
                "inputValues": merged_inputs
            },
            polling_options=polling_options
        )

    def _merge_input_values(
        self,
        preset_inputs: Optional[Dict[str, Any]],
        user_inputs: Optional[TaskInputValues]
    ) -> TaskInputValues:
        """Merge preset parameters and user parameters

        User parameters take priority, parameters not provided use preset values.

        Args:
            preset_inputs: Preset parameters (object format)
            user_inputs: User parameters (supports three formats)

        Returns:
            Merged parameters
        """
        if not preset_inputs or len(preset_inputs) == 0:
            return user_inputs or {}

        if not user_inputs:
            return preset_inputs

        # Normalize user parameters to object format
        normalized_user_inputs = self._normalize_to_object(user_inputs)

        # Merge parameters (user parameters take priority)
        return {**preset_inputs, **normalized_user_inputs}

    def _normalize_to_object(self, input_values: TaskInputValues) -> Dict[str, Any]:
        """Normalize TaskInputValues to object format

        Supports three formats:
        1. Object format: {"input1": "value1"}
        2. InputValue array: [{"handle": "input1", "value": "value1"}]
        3. NodeInputs array: [{"nodeId": "node1", "inputs": [...]}]

        Args:
            input_values: Input values

        Returns:
            Input values in object format
        """
        # Format 1: Object format
        if isinstance(input_values, dict):
            return input_values

        # Format 2 and 3: List format
        if isinstance(input_values, list):
            if len(input_values) > 0:
                first_item = input_values[0]

                # Format 2: InputValue array
                if "handle" in first_item:
                    return {item["handle"]: item["value"] for item in input_values}

                # Format 3: NodeInputs array (use the first node)
                if "nodeId" in first_item and "inputs" in first_item:
                    return {
                        item["handle"]: item["value"]
                        for item in first_item["inputs"]
                    }

        return {}

    def _extract_package_name(self, package_id: str) -> str:
        """Extract package name from packageId (remove version number)

        Args:
            package_id: Package ID (format: "package-name-x.y.z")

        Returns:
            Package name (version number removed)

        Example:
            >>> _extract_package_name("json-repair-1.0.1")
            "json-repair"
            >>> _extract_package_name("ffmpeg-0.4.3")
            "ffmpeg"
        """
        return re.sub(r'-\d+\.\d+\.\d+$', '', package_id)
