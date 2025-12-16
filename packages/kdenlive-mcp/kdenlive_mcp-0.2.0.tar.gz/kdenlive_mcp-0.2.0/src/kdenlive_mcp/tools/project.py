"""Project management tools for Kdenlive MCP.

Tools for opening, saving, creating, and managing Kdenlive projects.
"""

from __future__ import annotations

from kdenlive_api.validators import ProjectOpenInput, ProjectSaveInput
from mcp.server.fastmcp import Context, FastMCP

from ._common import get_client, mcp_tool_wrapper


def register_project_tools(mcp: FastMCP) -> None:
    """Register project management tools."""

    @mcp.tool()
    @mcp_tool_wrapper
    async def project_get_info(ctx: Context) -> dict:
        """Get information about the current Kdenlive project.

        Returns project name, path, resolution, fps, duration, and modification status.
        """
        client = get_client(ctx)
        info = await client.project.get_info()
        return info.model_dump()

    @mcp.tool()
    @mcp_tool_wrapper
    async def project_open(ctx: Context, path: str) -> dict:
        """Open a Kdenlive project file.

        Args:
            path: Full path to the .kdenlive project file (must have .kdenlive extension)
        """
        validated = ProjectOpenInput(path=path)
        client = get_client(ctx)
        result = await client.project.open(validated.path)
        return result

    @mcp.tool()
    @mcp_tool_wrapper
    async def project_save(ctx: Context, path: str | None = None) -> dict:
        """Save the current project.

        Args:
            path: Optional new path to save to (must have .kdenlive extension if provided)
        """
        validated = ProjectSaveInput(path=path)
        client = get_client(ctx)
        result = await client.project.save(validated.path)
        return result

    @mcp.tool()
    @mcp_tool_wrapper
    async def project_close(ctx: Context, save_changes: bool = False) -> dict:
        """Close the current project.

        IMPORTANT: For automation, save_changes defaults to false to avoid blocking dialogs.
        Call project_save() explicitly before closing if you need to preserve changes.

        If save_changes=true and the project is modified, it will auto-save without prompting.

        Args:
            save_changes: Whether to save changes before closing (default: false for automation)
        """
        client = get_client(ctx)
        result = await client.project.close(save_changes)
        return result

    @mcp.tool()
    @mcp_tool_wrapper
    async def project_new(ctx: Context, profile: str | None = None) -> dict:
        """Create a new Kdenlive project.

        Args:
            profile: Optional video profile (e.g., 'atsc_1080p_25', 'atsc_1080p_30')
        """
        client = get_client(ctx)
        result = await client.project.new(profile)
        return result

    @mcp.tool()
    @mcp_tool_wrapper
    async def project_undo(ctx: Context) -> dict:
        """Undo the last action in Kdenlive."""
        client = get_client(ctx)
        result = await client.project.undo()
        return result

    @mcp.tool()
    @mcp_tool_wrapper
    async def project_redo(ctx: Context) -> dict:
        """Redo the last undone action in Kdenlive."""
        client = get_client(ctx)
        result = await client.project.redo()
        return result
