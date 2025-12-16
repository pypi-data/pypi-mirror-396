"""Blocks client"""

import re
from typing import TYPE_CHECKING, Optional

from .types import Block, ListBlocksResponse

if TYPE_CHECKING:
    from .client import OomolConnectClient


def extract_version_from_path(path: str) -> str:
    """Extract version number from path

    Args:
        path: Path to the block, e.g., "/home/user/.oomol/packages/ffmpeg/0.1.9/blocks/audio_video_separation"

    Returns:
        Version string, e.g., "0.1.9", returns "unknown" if extraction fails
    """
    # Match version number format in path (e.g., 0.1.9)
    match = re.search(r'/(\d+\.\d+\.\d+)/', path)
    if match:
        return match.group(1)
    return "unknown"


def filter_latest_versions(blocks: list[Block]) -> list[Block]:
    """Filter out the latest version of each package

    Args:
        blocks: List of all blocks

    Returns:
        Filtered list containing only the latest version blocks of each package
    """
    # Group by package
    package_blocks: dict[str, list[Block]] = {}
    for block in blocks:
        package = block["package"]
        if package not in package_blocks:
            package_blocks[package] = []
        package_blocks[package].append(block)

    # For each package, select the block with the highest version
    result: list[Block] = []
    for package, pkg_blocks in package_blocks.items():
        # Sort by version number (descending)
        sorted_blocks = sorted(
            pkg_blocks,
            key=lambda b: [int(x) for x in b["version"].split(".")] if b["version"] != "unknown" else [0, 0, 0],
            reverse=True
        )

        # Only take all blocks of the latest version
        if sorted_blocks:
            latest_version = sorted_blocks[0]["version"]
            latest_blocks = [b for b in sorted_blocks if b["version"] == latest_version]
            result.extend(latest_blocks)

    return result


class BlocksClient:
    """Blocks API client

    Used to list available blocks (primitive computation units) in the system.
    """

    def __init__(self, client: "OomolConnectClient") -> None:
        """Initialize Blocks client

        Args:
            client: Main client instance
        """
        self._client = client

    async def list(self, include_all_versions: bool = False) -> ListBlocksResponse:
        """List all available blocks

        Args:
            include_all_versions: Whether to include all versions. Default False returns only the latest version

        Returns:
            Response containing block list, each block automatically includes blockId and version fields

        Example:
            >>> # Get only the latest version (default)
            >>> blocks_response = await client.blocks.list()
            >>> for block in blocks_response["blocks"]:
            ...     print(f"{block['blockId']} - v{block['version']}")

            >>> # Get all versions
            >>> all_blocks = await client.blocks.list(include_all_versions=True)
        """
        response: ListBlocksResponse = await self._client.request("/v1/blocks", method="GET")

        # Add blockId and version fields to each block
        blocks = response["blocks"]
        for block in blocks:
            # Generate blockId
            block["blockId"] = f"{block['package']}::{block['name']}"
            # Extract version number
            block["version"] = extract_version_from_path(block["path"])

        # Filter versions based on parameter
        if not include_all_versions:
            blocks = filter_latest_versions(blocks)

        return {"blocks": blocks}
