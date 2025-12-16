"""Utility functions"""

import asyncio
from typing import Any, Dict, List
from urllib.parse import urljoin

from .types import InputValue, NodeInputs, TaskInputValues


def normalize_input_values(input_values: TaskInputValues) -> List[NodeInputs]:
    """Normalize input values to NodeInputs[] format

    Supports three formats:
    1. Object format: {"input1": "value1", "input2": 123}
    2. Array format: [{"handle": "input1", "value": "value1"}, ...]
    3. Node format: [{"nodeId": "node1", "inputs": [...]}]

    Args:
        input_values: Input values (one of three formats)

    Returns:
        Standardized NodeInputs list
    """
    if not input_values:
        return []

    # Format 3: Already in NodeInputs[] format
    if isinstance(input_values, list) and len(input_values) > 0:
        first = input_values[0]
        if isinstance(first, dict) and "nodeId" in first:
            return input_values  # type: ignore

    # Format 2: Array format [{"handle": ..., "value": ...}]
    if isinstance(input_values, list):
        return [
            NodeInputs(
                nodeId="_",
                inputs=input_values  # type: ignore
            )
        ]

    # Format 1: Object format {"input1": "value1"}
    if isinstance(input_values, dict):
        inputs: List[InputValue] = [
            InputValue(handle=key, value=value)
            for key, value in input_values.items()
        ]
        return [
            NodeInputs(
                nodeId="_",
                inputs=inputs
            )
        ]

    return []


def build_url(base_url: str, path: str) -> str:
    """Build complete URL

    Args:
        base_url: Base URL
        path: Path

    Returns:
        Complete URL
    """
    # Ensure base_url ends with /
    if not base_url.endswith("/"):
        base_url += "/"

    # Ensure path doesn't start with /
    if path.startswith("/"):
        path = path[1:]

    return urljoin(base_url, path)


async def sleep(ms: int) -> None:
    """Sleep for specified milliseconds

    Args:
        ms: Milliseconds
    """
    await asyncio.sleep(ms / 1000.0)


def extract_result_from_logs(logs: List[Any]) -> Any:
    """Extract result from logs

    Find BlockFinished type logs and extract the result from them

    Args:
        logs: Task log list

    Returns:
        Extracted result, returns None if not found
    """
    for log in reversed(logs):  # Search from the end for the newest result
        if isinstance(log, dict) and log.get("type") == "BlockFinished":
            event = log.get("event")
            if event and isinstance(event, dict):
                return event.get("result")
    return None
