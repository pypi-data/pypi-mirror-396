"""Tests for MCP server."""

from __future__ import annotations

from kdenlive_mcp.server import KdenliveContext, mcp


class TestMCPServer:
    """Test MCP server configuration."""

    def test_server_exists(self) -> None:
        """Test server is created."""
        assert mcp is not None

    def test_server_name(self) -> None:
        """Test server has correct name."""
        assert mcp.name == "Kdenlive MCP"

    def test_server_has_instructions(self) -> None:
        """Test server has instructions."""
        assert mcp.instructions is not None
        assert "Kdenlive" in mcp.instructions


class TestKdenliveContext:
    """Test KdenliveContext dataclass."""

    def test_context_creation(self) -> None:
        """Test creating context."""
        from kdenlive_api import KdenliveClient

        client = KdenliveClient(mock=True)
        ctx = KdenliveContext(client=client)

        assert ctx.client is client
