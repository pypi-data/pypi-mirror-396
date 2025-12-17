"""Bin management tools for Kdenlive MCP.

Tools for managing clips, folders, and markers in the project bin.
"""

from __future__ import annotations

from kdenlive_api.validators import (
    BinAddClipMarkerInput,
    BinCreateFolderInput,
    BinDeleteClipInput,
    BinDeleteClipMarkerInput,
    BinDeleteClipsInput,
    BinDeleteFolderInput,
    BinGetClipInfoInput,
    BinGetClipMarkersInput,
    BinImportClipInput,
    BinImportClipsInput,
    BinListClipsInput,
    BinMoveItemInput,
    BinRenameItemInput,
)
from mcp.server.fastmcp import Context, FastMCP

from ._common import get_client, mcp_tool_wrapper


def register_bin_tools(mcp: FastMCP) -> None:
    """Register bin management tools."""

    # ==========================================================================
    # Listing & Info
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_list_clips(ctx: Context, folder_id: str | None = None) -> list[dict]:
        """List clips in the project bin.

        Args:
            folder_id: Optional folder ID to filter by
        """
        validated = BinListClipsInput(folder_id=folder_id)
        client = get_client(ctx)
        clips = await client.bin.list_clips(validated.folder_id)
        return [c.model_dump() for c in clips]

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_list_folders(ctx: Context) -> list[dict]:
        """List folders in the project bin."""
        client = get_client(ctx)
        folders = await client.bin.list_folders()
        return [f.model_dump() for f in folders]

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_get_clip_info(ctx: Context, clip_id: str) -> dict:
        """Get detailed information about a clip.

        Args:
            clip_id: ID of the clip (non-empty string)
        """
        validated = BinGetClipInfoInput(clip_id=clip_id)
        client = get_client(ctx)
        info = await client.bin.get_clip_info(validated.clip_id)
        return info.model_dump()

    # ==========================================================================
    # Import
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_import_clip(
        ctx: Context,
        url: str,
        folder_id: str | None = None,
        server_timeout: int | None = None,
    ) -> dict:
        """Import a media file into the project bin.

        Args:
            url: Absolute path to the media file
            folder_id: Optional target folder ID
            server_timeout: Server timeout in ms (0=immediate return, None=default 10s, >0=custom)
        """
        validated = BinImportClipInput(url=url, folder_id=folder_id, server_timeout=server_timeout)
        client = get_client(ctx)
        clip_id = await client.bin.import_clip(
            validated.url, validated.folder_id, validated.server_timeout
        )
        return {"clipId": clip_id}

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_import_clips(
        ctx: Context,
        urls: list[str],
        folder_id: str | None = None,
        server_timeout: int | None = None,
    ) -> dict:
        """Import multiple media files into the project bin.

        Args:
            urls: List of absolute paths to media files (at least one required)
            folder_id: Optional target folder ID
            server_timeout: Server timeout in ms per clip (0=immediate return, None=default 10s)
        """
        validated = BinImportClipsInput(urls=urls, folder_id=folder_id, server_timeout=server_timeout)
        client = get_client(ctx)
        clip_ids = await client.bin.import_clips(
            validated.urls, validated.folder_id, validated.server_timeout
        )
        return {"clipIds": clip_ids}

    # ==========================================================================
    # Delete
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_delete_clip(ctx: Context, clip_id: str) -> dict:
        """Delete a clip from the bin.

        Args:
            clip_id: ID of the clip to delete (non-empty string)
        """
        validated = BinDeleteClipInput(clip_id=clip_id)
        client = get_client(ctx)
        result = await client.bin.delete_clip(validated.clip_id)
        return {"deleted": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_delete_clips(ctx: Context, clip_ids: list[str]) -> dict:
        """Delete multiple clips from the bin at once.

        More efficient than calling bin_delete_clip multiple times.

        Args:
            clip_ids: List of clip IDs to delete (at least one, all non-empty)
        """
        validated = BinDeleteClipsInput(clip_ids=clip_ids)
        client = get_client(ctx)
        count = await client.bin.delete_clips(validated.clip_ids)
        return {"deleted_count": count}

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_delete_folder(ctx: Context, folder_id: str) -> dict:
        """Delete a folder from the bin.

        Args:
            folder_id: ID of the folder to delete (non-empty string)
        """
        validated = BinDeleteFolderInput(folder_id=folder_id)
        client = get_client(ctx)
        result = await client.bin.delete_folder(validated.folder_id)
        return {"deleted": result}

    # ==========================================================================
    # Organization
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_create_folder(
        ctx: Context,
        name: str,
        parent_id: str | None = None,
    ) -> dict:
        """Create a folder in the project bin.

        Args:
            name: Name for the new folder (non-empty string)
            parent_id: Optional parent folder ID
        """
        validated = BinCreateFolderInput(name=name, parent_id=parent_id)
        client = get_client(ctx)
        folder_id = await client.bin.create_folder(validated.name, validated.parent_id)
        return {"folderId": folder_id}

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_rename_item(ctx: Context, item_id: str, name: str) -> dict:
        """Rename a clip or folder in the bin.

        Args:
            item_id: ID of the item to rename (non-empty string)
            name: New name (non-empty string)
        """
        validated = BinRenameItemInput(item_id=item_id, name=name)
        client = get_client(ctx)
        result = await client.bin.rename_item(validated.item_id, validated.name)
        return {"renamed": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_move_item(ctx: Context, item_id: str, target_folder_id: str) -> dict:
        """Move a clip or folder to a different folder.

        Args:
            item_id: ID of the item to move (non-empty string)
            target_folder_id: Target folder ID (non-empty string)
        """
        validated = BinMoveItemInput(item_id=item_id, target_folder_id=target_folder_id)
        client = get_client(ctx)
        result = await client.bin.move_item(validated.item_id, validated.target_folder_id)
        return {"moved": result}

    # ==========================================================================
    # Markers
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_get_clip_markers(ctx: Context, clip_id: str) -> list[dict]:
        """Get all markers on a clip.

        Args:
            clip_id: ID of the clip (non-empty string)
        """
        validated = BinGetClipMarkersInput(clip_id=clip_id)
        client = get_client(ctx)
        markers = await client.bin.get_clip_markers(validated.clip_id)
        return [m.model_dump() for m in markers]

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_add_clip_marker(
        ctx: Context, clip_id: str, position: int, comment: str = ""
    ) -> dict:
        """Add a marker to a clip.

        Args:
            clip_id: ID of the clip (non-empty string)
            position: Marker position in frames (must be >= 0)
            comment: Optional marker comment
        """
        validated = BinAddClipMarkerInput(clip_id=clip_id, position=position, comment=comment)
        client = get_client(ctx)
        marker_id = await client.bin.add_clip_marker(
            validated.clip_id, validated.position, validated.comment
        )
        return {"markerId": marker_id}

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_delete_clip_marker(ctx: Context, clip_id: str, marker_id: int) -> dict:
        """Delete a marker from a clip.

        Args:
            clip_id: ID of the clip (non-empty string)
            marker_id: ID of the marker to delete (must be >= 0)
        """
        validated = BinDeleteClipMarkerInput(clip_id=clip_id, marker_id=marker_id)
        client = get_client(ctx)
        result = await client.bin.delete_clip_marker(validated.clip_id, validated.marker_id)
        return {"deleted": result}
