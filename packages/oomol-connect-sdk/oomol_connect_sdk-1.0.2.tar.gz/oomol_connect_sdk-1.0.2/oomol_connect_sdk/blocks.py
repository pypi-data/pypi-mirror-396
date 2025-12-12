"""Blocks 客户端"""

import re
from typing import TYPE_CHECKING, Optional

from .types import Block, ListBlocksResponse

if TYPE_CHECKING:
    from .client import OomolConnectClient


def extract_version_from_path(path: str) -> str:
    """从路径中提取版本号

    Args:
        path: block 的路径，例如 "/home/user/.oomol/packages/ffmpeg/0.1.9/blocks/audio_video_separation"

    Returns:
        版本号字符串，例如 "0.1.9"，如果无法提取则返回 "unknown"
    """
    # 匹配路径中的版本号格式（例如 0.1.9）
    match = re.search(r'/(\d+\.\d+\.\d+)/', path)
    if match:
        return match.group(1)
    return "unknown"


def filter_latest_versions(blocks: list[Block]) -> list[Block]:
    """过滤出每个 package 的最新版本

    Args:
        blocks: 所有 block 的列表

    Returns:
        过滤后只包含每个 package 最新版本的 block 列表
    """
    # 按 package 分组
    package_blocks: dict[str, list[Block]] = {}
    for block in blocks:
        package = block["package"]
        if package not in package_blocks:
            package_blocks[package] = []
        package_blocks[package].append(block)

    # 对每个 package，选择版本号最高的 block
    result: list[Block] = []
    for package, pkg_blocks in package_blocks.items():
        # 按版本号排序（降序）
        sorted_blocks = sorted(
            pkg_blocks,
            key=lambda b: [int(x) for x in b["version"].split(".")] if b["version"] != "unknown" else [0, 0, 0],
            reverse=True
        )

        # 只取最新版本的所有 blocks
        if sorted_blocks:
            latest_version = sorted_blocks[0]["version"]
            latest_blocks = [b for b in sorted_blocks if b["version"] == latest_version]
            result.extend(latest_blocks)

    return result


class BlocksClient:
    """Blocks API 客户端

    用于列出系统中可用的区块（原始计算单元）。
    """

    def __init__(self, client: "OomolConnectClient") -> None:
        """初始化 Blocks 客户端

        Args:
            client: 主客户端实例
        """
        self._client = client

    async def list(self, include_all_versions: bool = False) -> ListBlocksResponse:
        """列出所有可用的区块

        Args:
            include_all_versions: 是否包含所有版本。默认 False 只返回最新版本

        Returns:
            包含区块列表的响应，每个 block 自动包含 blockId 和 version 字段

        Example:
            >>> # 只获取最新版本（默认）
            >>> blocks_response = await client.blocks.list()
            >>> for block in blocks_response["blocks"]:
            ...     print(f"{block['blockId']} - v{block['version']}")

            >>> # 获取所有版本
            >>> all_blocks = await client.blocks.list(include_all_versions=True)
        """
        response: ListBlocksResponse = await self._client.request("/v1/blocks", method="GET")

        # 为每个 block 添加 blockId 和 version 字段
        blocks = response["blocks"]
        for block in blocks:
            # 生成 blockId
            block["blockId"] = f"{block['package']}::{block['name']}"
            # 提取版本号
            block["version"] = extract_version_from_path(block["path"])

        # 根据参数决定是否过滤版本
        if not include_all_versions:
            blocks = filter_latest_versions(blocks)

        return {"blocks": blocks}
