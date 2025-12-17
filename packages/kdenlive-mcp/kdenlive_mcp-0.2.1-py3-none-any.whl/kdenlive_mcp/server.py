"""MCP server for Kdenlive automation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from kdenlive_api import KdenliveClient
from mcp.server.fastmcp import FastMCP

from kdenlive_mcp.tools import register_tools


@dataclass
class KdenliveContext:
    """Application context with Kdenlive client."""

    client: KdenliveClient


@asynccontextmanager
async def kdenlive_lifespan(server: FastMCP) -> AsyncIterator[KdenliveContext]:
    """Manage Kdenlive client lifecycle."""
    client = KdenliveClient()
    try:
        await client.connect()
        yield KdenliveContext(client=client)
    finally:
        await client.disconnect()


# Create the MCP server
mcp = FastMCP(
    "Kdenlive MCP",
    instructions=(
        "MCP server for controlling Kdenlive video editor. "
        "Provides tools for project management, timeline editing, "
        "clip management, effects, and rendering."
    ),
    lifespan=kdenlive_lifespan,
)

# Register all tools
register_tools(mcp)


def main() -> None:
    """Entry point for kdenlive-mcp command."""
    mcp.run()


if __name__ == "__main__":
    main()
