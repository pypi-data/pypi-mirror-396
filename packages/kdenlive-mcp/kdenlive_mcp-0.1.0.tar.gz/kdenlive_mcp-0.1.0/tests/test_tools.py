"""Tests for MCP tools."""

from __future__ import annotations

from kdenlive_mcp.server import mcp


class TestToolRegistration:
    """Test that tools are properly registered."""

    def test_tools_registered(self) -> None:
        """Test tools are registered with server."""
        # FastMCP stores tools internally
        assert hasattr(mcp, "_tool_manager")

    def test_project_tools_exist(self) -> None:
        """Test project tools are registered."""
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        assert "project_get_info" in tool_names
        assert "project_open" in tool_names
        assert "project_save" in tool_names
        assert "project_close" in tool_names
        assert "project_new" in tool_names
        assert "project_undo" in tool_names
        assert "project_redo" in tool_names

    def test_timeline_tools_exist(self) -> None:
        """Test timeline tools are registered."""
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        assert "timeline_get_info" in tool_names
        assert "timeline_get_tracks" in tool_names
        assert "timeline_get_clips" in tool_names
        assert "timeline_insert_clip" in tool_names
        assert "timeline_move_clip" in tool_names
        assert "timeline_delete_clip" in tool_names

    def test_bin_tools_exist(self) -> None:
        """Test bin tools are registered."""
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        assert "bin_list_clips" in tool_names
        assert "bin_list_folders" in tool_names
        assert "bin_import_clip" in tool_names
        assert "bin_delete_clip" in tool_names

    def test_effects_tools_exist(self) -> None:
        """Test effects tools are registered."""
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        assert "effect_list_available" in tool_names
        assert "effect_add" in tool_names
        assert "effect_remove" in tool_names

    def test_render_tools_exist(self) -> None:
        """Test render tools are registered."""
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        assert "render_get_presets" in tool_names
        assert "render_start" in tool_names
        assert "render_stop" in tool_names
        assert "render_get_status" in tool_names

    def test_utility_tools_exist(self) -> None:
        """Test utility tools are registered."""
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        assert "kdenlive_ping" in tool_names
        assert "kdenlive_version" in tool_names


class TestToolCount:
    """Test tool counts."""

    def test_minimum_tools_registered(self) -> None:
        """Test at least 50 tools are registered."""
        tool_count = len(mcp._tool_manager._tools)
        assert tool_count >= 50, f"Expected at least 50 tools, got {tool_count}"


class TestToolDescriptions:
    """Test tool descriptions."""

    def test_tools_have_descriptions(self) -> None:
        """Test all tools have descriptions."""
        for tool in mcp._tool_manager._tools.values():
            assert tool.description, f"Tool {tool.name} missing description"

    def test_descriptions_not_empty(self) -> None:
        """Test descriptions are not empty."""
        for tool in mcp._tool_manager._tools.values():
            assert len(tool.description) > 10, f"Tool {tool.name} has very short description"
