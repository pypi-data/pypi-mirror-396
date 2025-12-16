"""MCP tool definitions for Kdenlive.

All tools validate input parameters using Pydantic models before calling
the kdenlive-api layer. This ensures type errors and usage errors are caught
early with clear error messages.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from kdenlive_api.exceptions import KdenliveError, ValidationError
from kdenlive_api.validators import (
    AssetFavoriteInput,
    AssetGetEffectsByCategoryInput,
    AssetGetPresetsInput,
    AssetSavePresetInput,
    AssetSearchInput,
    BinAddClipMarkerInput,
    BinCreateFolderInput,
    BinDeleteClipInput,
    BinDeleteClipMarkerInput,
    BinGetClipInfoInput,
    BinImportClipInput,
    BinImportClipsInput,
    BinListClipsInput,
    BinMoveItemInput,
    BinRenameItemInput,
    CompositionAddInput,
    CompositionRemoveInput,
    EffectAddInput,
    EffectEnableDisableInput,
    EffectGetClipEffectsInput,
    EffectGetInfoInput,
    EffectKeyframeInput,
    EffectRemoveInput,
    EffectSetKeyframeInput,
    EffectSetPropertyInput,
    ProjectOpenInput,
    ProjectSaveInput,
    RenderGetStatusInput,
    RenderStartInput,
    RenderStopInput,
    TimelineAddTrackInput,
    TimelineDeleteClipInput,
    TimelineDeleteTrackInput,
    TimelineGetClipsInput,
    TimelineInsertClipInput,
    TimelineMoveClipInput,
    TimelineResizeClipInput,
    TimelineSeekInput,
    TimelineSplitClipInput,
    TransitionAddInput,
    TransitionRemoveInput,
)
from mcp.server.fastmcp import Context, FastMCP
from pydantic import ValidationError as PydanticValidationError

T = TypeVar("T")


def get_client(ctx: Context):
    """Get Kdenlive client from context."""
    return ctx.request_context.lifespan_context.client


def format_validation_error(e: PydanticValidationError) -> str:
    """Format Pydantic validation error into a readable message."""
    errors = e.errors()
    if len(errors) == 1:
        err = errors[0]
        loc = ".".join(str(x) for x in err["loc"]) if err["loc"] else "input"
        return f"Invalid {loc}: {err['msg']}"
    else:
        messages = []
        for err in errors:
            loc = ".".join(str(x) for x in err["loc"]) if err["loc"] else "input"
            messages.append(f"  - {loc}: {err['msg']}")
        return "Validation errors:\n" + "\n".join(messages)


def mcp_tool_wrapper(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to wrap MCP tools with error handling.

    Catches validation errors and Kdenlive errors, returning them as
    structured error responses instead of raising exceptions.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> dict[str, Any] | list[dict] | None:
        try:
            return await func(*args, **kwargs)
        except PydanticValidationError as e:
            return {"error": format_validation_error(e), "code": -32602}
        except ValidationError as e:
            return {"error": str(e), "code": e.code}
        except KdenliveError as e:
            return {"error": str(e), "code": e.code}
        except ValueError as e:
            return {"error": str(e), "code": -32602}
        except Exception as e:
            return {"error": f"Unexpected error: {e}", "code": -32603}

    return wrapper


def register_tools(mcp: FastMCP) -> None:
    """Register all Kdenlive tools with the MCP server."""

    # ==========================================================================
    # Project Tools
    # ==========================================================================

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
    async def project_close(ctx: Context, save_changes: bool = True) -> dict:
        """Close the current project.

        Args:
            save_changes: Whether to save changes before closing (default: true)
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

    # ==========================================================================
    # Timeline Tools
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
    async def timeline_seek(ctx: Context, position: int) -> dict:
        """Move the playhead to a specific position.

        Args:
            position: Target position in frames (must be >= 0)
        """
        validated = TimelineSeekInput(position=position)
        client = get_client(ctx)
        result = await client.timeline.seek(validated.position)
        return {"position": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def timeline_get_position(ctx: Context) -> dict:
        """Get the current playhead position."""
        client = get_client(ctx)
        position = await client.timeline.get_position()
        return {"position": position}

    # ==========================================================================
    # Bin Tools
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

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_import_clip(
        ctx: Context,
        url: str,
        folder_id: str | None = None,
    ) -> dict:
        """Import a media file into the project bin.

        Args:
            url: Absolute path to the media file
            folder_id: Optional target folder ID
        """
        validated = BinImportClipInput(url=url, folder_id=folder_id)
        client = get_client(ctx)
        clip_id = await client.bin.import_clip(validated.url, validated.folder_id)
        return {"clipId": clip_id}

    @mcp.tool()
    @mcp_tool_wrapper
    async def bin_import_clips(
        ctx: Context,
        urls: list[str],
        folder_id: str | None = None,
    ) -> dict:
        """Import multiple media files into the project bin.

        Args:
            urls: List of absolute paths to media files (at least one required)
            folder_id: Optional target folder ID
        """
        validated = BinImportClipsInput(urls=urls, folder_id=folder_id)
        client = get_client(ctx)
        clip_ids = await client.bin.import_clips(validated.urls, validated.folder_id)
        return {"clipIds": clip_ids}

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

    # ==========================================================================
    # Effects Tools
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_list_available(ctx: Context) -> list[dict]:
        """List all available effects in Kdenlive."""
        client = get_client(ctx)
        effects = await client.effects.list_available()
        return [e.model_dump() for e in effects]

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_get_info(ctx: Context, effect_id: str) -> dict:
        """Get detailed information about an effect including parameters.

        Args:
            effect_id: ID of the effect (non-empty string)
        """
        validated = EffectGetInfoInput(effect_id=effect_id)
        client = get_client(ctx)
        info = await client.effects.get_info(validated.effect_id)
        return info.model_dump()

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_add(ctx: Context, effect_id: str, clip_id: int) -> dict:
        """Add an effect to a clip on the timeline.

        Args:
            effect_id: ID of the effect to add (non-empty string)
            clip_id: ID of the target clip (must be >= 0)
        """
        validated = EffectAddInput(effect_id=effect_id, clip_id=clip_id)
        client = get_client(ctx)
        instance_id = await client.effects.add(validated.effect_id, validated.clip_id)
        return {"effectInstanceId": instance_id}

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_remove(ctx: Context, clip_id: int, effect_id: str) -> dict:
        """Remove an effect from a clip.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect instance to remove (non-empty string)
        """
        validated = EffectRemoveInput(clip_id=clip_id, effect_id=effect_id)
        client = get_client(ctx)
        result = await client.effects.remove(validated.clip_id, validated.effect_id)
        return {"deleted": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_get_clip_effects(ctx: Context, clip_id: int) -> list[dict]:
        """List all effects applied to a clip.

        Args:
            clip_id: ID of the clip (must be >= 0)
        """
        validated = EffectGetClipEffectsInput(clip_id=clip_id)
        client = get_client(ctx)
        effects = await client.effects.get_clip_effects(validated.clip_id)
        return [e.model_dump() for e in effects]

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_set_property(
        ctx: Context,
        clip_id: int,
        effect_id: str,
        property_name: str,
        value: Any,
    ) -> dict:
        """Set an effect parameter value.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect instance (non-empty string)
            property_name: Name of the property to set (non-empty string)
            value: New value for the property
        """
        validated = EffectSetPropertyInput(
            clip_id=clip_id, effect_id=effect_id, property_name=property_name, value=value
        )
        client = get_client(ctx)
        result = await client.effects.set_property(
            validated.clip_id, validated.effect_id, validated.property_name, validated.value
        )
        return {"updated": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_enable(ctx: Context, clip_id: int, effect_id: str) -> dict:
        """Enable an effect on a clip.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect instance (non-empty string)
        """
        validated = EffectEnableDisableInput(clip_id=clip_id, effect_id=effect_id)
        client = get_client(ctx)
        result = await client.effects.enable(validated.clip_id, validated.effect_id)
        return {"enabled": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_disable(ctx: Context, clip_id: int, effect_id: str) -> dict:
        """Disable an effect on a clip.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect instance (non-empty string)
        """
        validated = EffectEnableDisableInput(clip_id=clip_id, effect_id=effect_id)
        client = get_client(ctx)
        result = await client.effects.disable(validated.clip_id, validated.effect_id)
        return {"disabled": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_get_keyframes(
        ctx: Context, clip_id: int, effect_id: str, property_name: str
    ) -> dict:
        """Get keyframes for an effect parameter.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect (non-empty string)
            property_name: Name of the property (non-empty string)
        """
        validated = EffectKeyframeInput(
            clip_id=clip_id, effect_id=effect_id, property_name=property_name, position=0
        )
        client = get_client(ctx)
        keyframes = await client.effects.get_keyframes(
            validated.clip_id, validated.effect_id, validated.property_name
        )
        return {"keyframes": [k.model_dump() for k in keyframes]}

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_set_keyframe(
        ctx: Context, clip_id: int, effect_id: str, property_name: str, position: int, value: Any
    ) -> dict:
        """Set or add a keyframe for an effect parameter.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect (non-empty string)
            property_name: Name of the property (non-empty string)
            position: Keyframe position in frames (must be >= 0)
            value: Keyframe value
        """
        validated = EffectSetKeyframeInput(
            clip_id=clip_id,
            effect_id=effect_id,
            property_name=property_name,
            position=position,
            value=value,
        )
        client = get_client(ctx)
        result = await client.effects.set_keyframe(
            validated.clip_id,
            validated.effect_id,
            validated.property_name,
            validated.position,
            validated.value,
        )
        return {"updated": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_delete_keyframe(
        ctx: Context, clip_id: int, effect_id: str, property_name: str, position: int
    ) -> dict:
        """Delete a keyframe at a specific position.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect (non-empty string)
            property_name: Name of the property (non-empty string)
            position: Keyframe position to delete (must be >= 0)
        """
        validated = EffectKeyframeInput(
            clip_id=clip_id, effect_id=effect_id, property_name=property_name, position=position
        )
        client = get_client(ctx)
        result = await client.effects.delete_keyframe(
            validated.clip_id, validated.effect_id, validated.property_name, validated.position
        )
        return {"deleted": result}

    # ==========================================================================
    # Render Tools
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def render_get_presets(ctx: Context) -> list[dict]:
        """List available render presets."""
        client = get_client(ctx)
        presets = await client.render.get_presets()
        return [p.model_dump() for p in presets]

    @mcp.tool()
    @mcp_tool_wrapper
    async def render_start(
        ctx: Context,
        preset_name: str,
        output_path: str,
    ) -> dict:
        """Start a render job.

        Args:
            preset_name: Name of the render preset to use (non-empty string)
            output_path: Absolute path for the output file
        """
        validated = RenderStartInput(preset_name=preset_name, output_path=output_path)
        client = get_client(ctx)
        job = await client.render.start(validated.preset_name, validated.output_path)
        return job.model_dump()

    @mcp.tool()
    @mcp_tool_wrapper
    async def render_stop(ctx: Context, job_id: str) -> dict:
        """Stop a render job.

        Args:
            job_id: ID of the job to stop (non-empty string)
        """
        validated = RenderStopInput(job_id=job_id)
        client = get_client(ctx)
        result = await client.render.stop(validated.job_id)
        return {"stopped": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def render_get_status(ctx: Context, job_id: str) -> dict:
        """Get the status of a render job.

        Args:
            job_id: ID of the job (non-empty string)
        """
        validated = RenderGetStatusInput(job_id=job_id)
        client = get_client(ctx)
        status = await client.render.get_status(validated.job_id)
        return status.model_dump()

    @mcp.tool()
    @mcp_tool_wrapper
    async def render_get_jobs(ctx: Context) -> list[dict]:
        """List all render jobs."""
        client = get_client(ctx)
        jobs = await client.render.get_jobs()
        return [j.model_dump() for j in jobs]

    @mcp.tool()
    @mcp_tool_wrapper
    async def render_get_active_job(ctx: Context) -> dict | None:
        """Get the currently active render job, if any."""
        client = get_client(ctx)
        job = await client.render.get_active_job()
        return job.model_dump() if job else None

    # ==========================================================================
    # Asset Tools
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_list_categories(ctx: Context) -> list[dict]:
        """List effect/transition categories."""
        client = get_client(ctx)
        categories = await client.asset.list_categories()
        return [c.model_dump() for c in categories]

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_search(ctx: Context, query: str) -> list[dict]:
        """Search for effects and transitions.

        Args:
            query: Search query string (non-empty)
        """
        validated = AssetSearchInput(query=query)
        client = get_client(ctx)
        results = await client.asset.search(validated.query)
        return [r.model_dump() for r in results]

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_get_effects_by_category(ctx: Context, category: str) -> list[dict]:
        """Get effects in a specific category.

        Args:
            category: Name of the category (non-empty string)
        """
        validated = AssetGetEffectsByCategoryInput(category=category)
        client = get_client(ctx)
        effects = await client.asset.get_effects_by_category(validated.category)
        return [e.model_dump() for e in effects]

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_get_favorites(ctx: Context) -> list[dict]:
        """Get user's favorite effects and transitions."""
        client = get_client(ctx)
        favorites = await client.asset.get_favorites()
        return [f.model_dump() for f in favorites]

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_add_favorite(ctx: Context, asset_id: str) -> dict:
        """Add an asset to favorites.

        Args:
            asset_id: ID of the asset (non-empty string)
        """
        validated = AssetFavoriteInput(asset_id=asset_id)
        client = get_client(ctx)
        result = await client.asset.add_favorite(validated.asset_id)
        return {"added": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_remove_favorite(ctx: Context, asset_id: str) -> dict:
        """Remove an asset from favorites.

        Args:
            asset_id: ID of the asset (non-empty string)
        """
        validated = AssetFavoriteInput(asset_id=asset_id)
        client = get_client(ctx)
        result = await client.asset.remove_favorite(validated.asset_id)
        return {"removed": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_get_presets(ctx: Context, effect_id: str) -> list[dict]:
        """Get presets for an effect.

        Args:
            effect_id: ID of the effect (non-empty string)
        """
        validated = AssetGetPresetsInput(effect_id=effect_id)
        client = get_client(ctx)
        presets = await client.asset.get_presets(validated.effect_id)
        return [p.model_dump() for p in presets]

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_save_preset(
        ctx: Context, effect_id: str, preset_name: str, clip_id: int
    ) -> dict:
        """Save effect settings as a preset.

        Args:
            effect_id: ID of the effect (non-empty string)
            preset_name: Name for the preset (non-empty string)
            clip_id: Source clip ID (must be >= 0)
        """
        validated = AssetSavePresetInput(
            effect_id=effect_id, preset_name=preset_name, clip_id=clip_id
        )
        client = get_client(ctx)
        result = await client.asset.save_preset(
            validated.effect_id, validated.preset_name, validated.clip_id
        )
        return {"saved": result}

    # ==========================================================================
    # Transition Tools
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def transition_list(ctx: Context) -> list[dict]:
        """List available transition types."""
        client = get_client(ctx)
        transitions = await client.transition.list()
        return [t.model_dump() for t in transitions]

    @mcp.tool()
    @mcp_tool_wrapper
    async def transition_add(
        ctx: Context,
        transition_type: str,
        from_clip_id: int,
        to_clip_id: int,
    ) -> dict:
        """Add a transition between two clips.

        Args:
            transition_type: Type of transition to add (non-empty string)
            from_clip_id: ID of the first clip (must be >= 0)
            to_clip_id: ID of the second clip (must be >= 0, different from from_clip_id)
        """
        validated = TransitionAddInput(
            transition_type=transition_type, from_clip_id=from_clip_id, to_clip_id=to_clip_id
        )
        client = get_client(ctx)
        info = await client.transition.add(
            validated.transition_type, validated.from_clip_id, validated.to_clip_id
        )
        return info.model_dump()

    @mcp.tool()
    @mcp_tool_wrapper
    async def transition_remove(ctx: Context, transition_id: int) -> dict:
        """Remove a transition.

        Args:
            transition_id: ID of the transition to remove (must be >= 0)
        """
        validated = TransitionRemoveInput(transition_id=transition_id)
        client = get_client(ctx)
        result = await client.transition.remove(validated.transition_id)
        return {"deleted": result}

    # ==========================================================================
    # Composition Tools
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def composition_list(ctx: Context) -> list[dict]:
        """List compositions on the timeline."""
        client = get_client(ctx)
        compositions = await client.composition.list()
        return [c.model_dump() for c in compositions]

    @mcp.tool()
    @mcp_tool_wrapper
    async def composition_add(
        ctx: Context,
        composition_type: str,
        track: int,
        position: int,
    ) -> dict:
        """Add a composition to the timeline.

        Args:
            composition_type: Type of composition (non-empty string)
            track: Target track number (must be >= 0)
            position: Position in frames (must be >= 0)
        """
        validated = CompositionAddInput(
            composition_type=composition_type, track=track, position=position
        )
        client = get_client(ctx)
        info = await client.composition.add(
            validated.composition_type, validated.track, validated.position
        )
        return info.model_dump()

    @mcp.tool()
    @mcp_tool_wrapper
    async def composition_remove(ctx: Context, composition_id: int) -> dict:
        """Remove a composition.

        Args:
            composition_id: ID of the composition to remove (must be >= 0)
        """
        validated = CompositionRemoveInput(composition_id=composition_id)
        client = get_client(ctx)
        result = await client.composition.remove(validated.composition_id)
        return {"deleted": result}

    # ==========================================================================
    # Utility Tools
    # ==========================================================================

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
