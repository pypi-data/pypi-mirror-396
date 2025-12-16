"""Utility tools for Kdenlive MCP.

Connection and diagnostic tools.
"""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from ._common import get_client, mcp_tool_wrapper


def register_utility_tools(mcp: FastMCP) -> None:
    """Register utility tools."""

    @mcp.tool()
    @mcp_tool_wrapper
    async def kdenlive_ping(ctx: Context) -> dict:
        """Check if Kdenlive is responding."""
        client = get_client(ctx)
        result = await client.ping()
        return {"connected": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def kdenlive_version(ctx: Context) -> dict:
        """Get Kdenlive and RPC server version information."""
        client = get_client(ctx)
        return await client.get_version()
