"""Timeline tools for Kdenlive MCP.

Tools for timeline manipulation including clips, tracks, and playhead control.
"""

from __future__ import annotations

from kdenlive_api.validators import (
    TimelineAddTrackInput,
    TimelineDeleteClipInput,
    TimelineDeleteClipsInput,
    TimelineDeleteTrackInput,
    TimelineGetClipsInput,
    TimelineInsertClipInput,
    TimelineMoveClipInput,
    TimelineResizeClipInput,
    TimelineSeekInput,
    TimelineSetSelectionInput,
    TimelineSetTrackPropertyInput,
    TimelineSplitClipInput,
)
from mcp.server.fastmcp import Context, FastMCP

from ._common import get_client, mcp_tool_wrapper


def register_timeline_tools(mcp: FastMCP) -> None:
    """Register timeline tools."""

    # ==========================================================================
    # Timeline Info
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_get_info(ctx: Context) -> dict:
        """Get timeline information including duration, track count, and current position."""
        client = get_client(ctx)
        info = await client.timeline.get_info()
        return info.model_dump()

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_get_tracks(ctx: Context) -> list[dict]:
        """Get all tracks on the timeline with their properties."""
        client = get_client(ctx)
        tracks = await client.timeline.get_tracks()
        return [t.model_dump() for t in tracks]

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_get_position(ctx: Context) -> dict:
        """Get the current playhead position."""
        client = get_client(ctx)
        position = await client.timeline.get_position()
        return {"position": position}

    # ==========================================================================
    # Clip Operations
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_get_clips(ctx: Context, track_id: int | None = None) -> list[dict]:
        """Get clips on the timeline.

        Args:
            track_id: Optional track ID to filter clips by (must be >= 0 if provided)
        """
        validated = TimelineGetClipsInput(track_id=track_id)
        client = get_client(ctx)
        clips = await client.timeline.get_clips(validated.track_id)
        return [c.model_dump() for c in clips]

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_get_clip(ctx: Context, clip_id: int) -> dict:
        """Get detailed information about a single clip.

        Args:
            clip_id: ID of the clip to get info for (must be >= 0)
        """
        validated = TimelineDeleteClipInput(clip_id=clip_id)  # Reuse for simple int validation
        client = get_client(ctx)
        clip = await client.timeline.get_clip(validated.clip_id)
        return clip.model_dump()

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_insert_clip(
        ctx: Context,
        bin_clip_id: str,
        track_id: int,
        position: int,
    ) -> dict:
        """Insert a clip from the bin onto the timeline.

        Args:
            bin_clip_id: ID of the clip in the bin (non-empty string)
            track_id: Target track ID (must be >= 0)
            position: Position in frames where to insert (must be >= 0)
        """
        validated = TimelineInsertClipInput(
            bin_clip_id=bin_clip_id, track_id=track_id, position=position
        )
        client = get_client(ctx)
        clip_id = await client.timeline.insert_clip(
            validated.bin_clip_id, validated.track_id, validated.position
        )
        return {"clipId": clip_id}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_move_clip(
        ctx: Context,
        clip_id: int,
        track_id: int,
        position: int,
    ) -> dict:
        """Move a clip to a new position/track.

        Args:
            clip_id: ID of the clip to move (must be >= 0)
            track_id: Target track ID (must be >= 0)
            position: New position in frames (must be >= 0)
        """
        validated = TimelineMoveClipInput(clip_id=clip_id, track_id=track_id, position=position)
        client = get_client(ctx)
        result = await client.timeline.move_clip(
            validated.clip_id, validated.track_id, validated.position
        )
        return {"moved": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_delete_clip(ctx: Context, clip_id: int) -> dict:
        """Delete a clip from the timeline.

        Args:
            clip_id: ID of the clip to delete (must be >= 0)
        """
        validated = TimelineDeleteClipInput(clip_id=clip_id)
        client = get_client(ctx)
        result = await client.timeline.delete_clip(validated.clip_id)
        return {"deleted": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_delete_clips(ctx: Context, clip_ids: list[int]) -> dict:
        """Delete multiple clips from the timeline at once.

        More efficient than calling timeline_delete_clip multiple times.

        Args:
            clip_ids: List of clip IDs to delete (at least one, all must be >= 0)
        """
        validated = TimelineDeleteClipsInput(clip_ids=clip_ids)
        client = get_client(ctx)
        count = await client.timeline.delete_clips(validated.clip_ids)
        return {"deleted_count": count}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_split_clip(ctx: Context, clip_id: int, position: int) -> dict:
        """Split a clip at a specific position.

        Args:
            clip_id: ID of the clip to split (must be >= 0)
            position: Position in frames where to split (must be >= 0)
        """
        validated = TimelineSplitClipInput(clip_id=clip_id, position=position)
        client = get_client(ctx)
        parts = await client.timeline.split_clip(validated.clip_id, validated.position)
        return {"parts": parts}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_resize_clip(
        ctx: Context,
        clip_id: int,
        in_point: int,
        out_point: int,
    ) -> dict:
        """Change clip in/out points (trim clip).

        Args:
            clip_id: ID of the clip to resize (must be >= 0)
            in_point: New in point in frames (must be >= 0)
            out_point: New out point in frames (must be > in_point)
        """
        validated = TimelineResizeClipInput(clip_id=clip_id, in_point=in_point, out_point=out_point)
        client = get_client(ctx)
        result = await client.timeline.resize_clip(
            validated.clip_id, validated.in_point, validated.out_point
        )
        return {"resized": result}

    # ==========================================================================
    # Selection
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_get_selection(ctx: Context) -> dict:
        """Get the IDs of currently selected clips on the timeline."""
        client = get_client(ctx)
        clip_ids = await client.timeline.get_selection()
        return {"clip_ids": clip_ids}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_set_selection(ctx: Context, clip_ids: list[int]) -> dict:
        """Select specific clips on the timeline.

        Pass an empty list to clear the selection.

        Args:
            clip_ids: List of clip IDs to select (all must be >= 0)
        """
        validated = TimelineSetSelectionInput(clip_ids=clip_ids)
        client = get_client(ctx)
        result = await client.timeline.set_selection(validated.clip_ids)
        return {"selected": result}

    # ==========================================================================
    # Track Management
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_add_track(
        ctx: Context,
        track_type: str,
        name: str | None = None,
    ) -> dict:
        """Add a new track to the timeline.

        Args:
            track_type: Type of track - must be 'video' or 'audio'
            name: Optional name for the track
        """
        validated = TimelineAddTrackInput(track_type=track_type, name=name)  # type: ignore[arg-type]
        client = get_client(ctx)
        track_id = await client.timeline.add_track(validated.track_type, validated.name)
        return {"trackId": track_id}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_delete_track(ctx: Context, track_id: int) -> dict:
        """Delete a track from the timeline.

        Args:
            track_id: ID of the track to delete (must be >= 0)
        """
        validated = TimelineDeleteTrackInput(track_id=track_id)
        client = get_client(ctx)
        result = await client.timeline.delete_track(validated.track_id)
        return {"deleted": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_set_track_property(
        ctx: Context,
        track_id: int,
        property_name: str,
        value: str | bool,
    ) -> dict:
        """Set a track property like name, locked, muted, or hidden.

        Args:
            track_id: ID of the track (must be >= 0)
            property_name: Property to set - 'name', 'locked', 'muted', or 'hidden'
            value: Property value (string for name, bool for others)
        """
        validated = TimelineSetTrackPropertyInput(
            track_id=track_id,
            property_name=property_name,  # type: ignore[arg-type]
            value=value,
        )
        client = get_client(ctx)
        result = await client.timeline.set_track_property(
            validated.track_id, validated.property_name, validated.value
        )
        return {"updated": result}

    # ==========================================================================
    # Playhead
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_seek(ctx: Context, position: int) -> dict:
        """Move the playhead to a specific position.

        Args:
            position: Target position in frames (must be >= 0)
        """
        validated = TimelineSeekInput(position=position)
        client = get_client(ctx)
        result = await client.timeline.seek(validated.position)
        return {"position": result}
