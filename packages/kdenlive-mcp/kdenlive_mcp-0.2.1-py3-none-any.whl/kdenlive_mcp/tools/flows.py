"""Flow tools for Kdenlive MCP.

Higher-level workflow tools that combine multiple API calls into atomic,
error-resistant operations. These reduce round-trips, prevent logic errors,
and simplify common multi-step workflows.
"""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from ._common import get_client, mcp_tool_wrapper


class FlowTransitionsInput(BaseModel):
    """Input for flow_add_transitions_between_clips."""

    track_id: int = Field(ge=0, description="Track ID")
    transition_type: str = Field(default="dissolve", min_length=1, description="Transition type")
    skip_gaps_larger_than: int = Field(
        default=30, ge=0, description="Skip gaps larger than N frames"
    )


class FlowApplyEffectInput(BaseModel):
    """Input for flow_apply_effect_to_track."""

    track_id: int = Field(ge=0, description="Track ID")
    effect_id: str = Field(min_length=1, description="Effect ID")


class FlowDeleteShortClipsInput(BaseModel):
    """Input for flow_delete_short_clips."""

    min_duration_frames: int = Field(ge=1, description="Minimum clip duration in frames")
    track_id: int | None = Field(default=None, ge=0, description="Optional track filter")


class FlowTrimAllClipsInput(BaseModel):
    """Input for flow_trim_all_clips."""

    track_id: int | None = Field(default=None, ge=0, description="Optional track filter")
    trim_start_frames: int = Field(default=0, ge=0, description="Frames to trim from start")
    trim_end_frames: int = Field(default=0, ge=0, description="Frames to trim from end")


class FlowFadeInOutInput(BaseModel):
    """Input for flow_add_fade_in_out."""

    fade_in_frames: int = Field(default=0, ge=0, description="Fade-in duration in frames")
    fade_out_frames: int = Field(default=0, ge=0, description="Fade-out duration in frames")
    all_clips: bool = Field(default=False, description="Apply to all clips, not just first/last")


class FlowExportAndWaitInput(BaseModel):
    """Input for flow_export_and_wait."""

    preset_name: str = Field(min_length=1, description="Render preset name")
    output_path: str = Field(min_length=1, description="Output file path")
    poll_interval_seconds: float = Field(default=2.0, ge=0.5, description="Polling interval")
    timeout_seconds: float = Field(default=3600.0, ge=10.0, description="Max wait time")


def register_flow_tools(mcp: FastMCP) -> None:
    """Register flow (workflow) tools."""

    # ==========================================================================
    # Timeline Flows
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def flow_add_transitions_between_clips(
        ctx: Context,
        track_id: int,
        transition_type: str = "dissolve",
        skip_gaps_larger_than: int = 30,
    ) -> dict:
        """Add transitions between all adjacent clips on a track.

        This flow tool automates the common task of adding consistent transitions
        between clips. It handles finding adjacent clips and only adds transitions
        where the gap is small enough.

        Args:
            track_id: Track to process (must be >= 0)
            transition_type: Type of transition to add (default: dissolve)
            skip_gaps_larger_than: Skip if gap between clips exceeds this (frames)
        """
        validated = FlowTransitionsInput(
            track_id=track_id,
            transition_type=transition_type,
            skip_gaps_larger_than=skip_gaps_larger_than,
        )
        client = get_client(ctx)

        # Get all clips on the track
        clips = await client.timeline.get_clips(validated.track_id)
        if len(clips) < 2:
            return {
                "added": 0,
                "message": "Need at least 2 clips on the track for transitions",
            }

        # Sort by position
        sorted_clips = sorted(clips, key=lambda c: c.position)

        added = 0
        errors: list[str] = []

        for i in range(len(sorted_clips) - 1):
            from_clip = sorted_clips[i]
            to_clip = sorted_clips[i + 1]

            # Calculate gap between clips
            gap = to_clip.position - (from_clip.position + from_clip.duration)
            if gap > validated.skip_gaps_larger_than:
                continue

            try:
                await client.transition.add(validated.transition_type, from_clip.id, to_clip.id)
                added += 1
            except Exception as e:
                errors.append(f"Clips {from_clip.id}->{to_clip.id}: {e}")

        return {
            "added": added,
            "total_clip_pairs": len(sorted_clips) - 1,
            "errors": errors if errors else None,
        }

    @mcp.tool()
    @mcp_tool_wrapper
    async def flow_apply_effect_to_track(
        ctx: Context,
        track_id: int,
        effect_id: str,
    ) -> dict:
        """Apply an effect to all clips on a track.

        This flow tool adds the same effect to every clip on a track,
        which is much faster than adding it clip-by-clip.

        Args:
            track_id: Track to process (must be >= 0)
            effect_id: ID of the effect to apply
        """
        validated = FlowApplyEffectInput(track_id=track_id, effect_id=effect_id)
        client = get_client(ctx)

        clips = await client.timeline.get_clips(validated.track_id)
        if not clips:
            return {"applied": 0, "message": "No clips on track"}

        applied = 0
        errors: list[str] = []

        for clip in clips:
            try:
                await client.effects.add(validated.effect_id, clip.id)
                applied += 1
            except Exception as e:
                errors.append(f"Clip {clip.id}: {e}")

        return {
            "applied": applied,
            "total_clips": len(clips),
            "errors": errors if errors else None,
        }

    @mcp.tool()
    @mcp_tool_wrapper
    async def flow_delete_short_clips(
        ctx: Context,
        min_duration_frames: int,
        track_id: int | None = None,
    ) -> dict:
        """Delete clips shorter than a minimum duration.

        Useful for cleaning up leftover tiny clips from editing.

        Args:
            min_duration_frames: Minimum clip duration in frames (clips shorter will be deleted)
            track_id: Optional track to filter (if None, checks all tracks)
        """
        validated = FlowDeleteShortClipsInput(
            min_duration_frames=min_duration_frames, track_id=track_id
        )
        client = get_client(ctx)

        clips = await client.timeline.get_clips(validated.track_id)

        # Find short clips
        short_clips = [c for c in clips if c.duration < validated.min_duration_frames]

        if not short_clips:
            return {"deleted": 0, "message": "No clips below threshold found"}

        # Delete using batch operation if available
        clip_ids = [c.id for c in short_clips]
        count = await client.timeline.delete_clips(clip_ids)

        return {
            "deleted": count,
            "total_checked": len(clips),
            "threshold_frames": validated.min_duration_frames,
        }

    @mcp.tool()
    @mcp_tool_wrapper
    async def flow_trim_all_clips(
        ctx: Context,
        track_id: int | None = None,
        trim_start_frames: int = 0,
        trim_end_frames: int = 0,
    ) -> dict:
        """Trim frames from the start and/or end of all clips.

        Useful for removing consistent lead-in/lead-out from footage.

        Args:
            track_id: Optional track to filter (if None, trims all clips)
            trim_start_frames: Frames to trim from start of each clip
            trim_end_frames: Frames to trim from end of each clip
        """
        validated = FlowTrimAllClipsInput(
            track_id=track_id,
            trim_start_frames=trim_start_frames,
            trim_end_frames=trim_end_frames,
        )

        if validated.trim_start_frames == 0 and validated.trim_end_frames == 0:
            return {"trimmed": 0, "message": "No trim values specified"}

        client = get_client(ctx)
        clips = await client.timeline.get_clips(validated.track_id)

        if not clips:
            return {"trimmed": 0, "message": "No clips found"}

        trimmed = 0
        skipped = 0
        errors: list[str] = []

        for clip in clips:
            # Calculate new in/out points
            new_in = clip.in_point + validated.trim_start_frames
            new_out = clip.out_point - validated.trim_end_frames

            # Validate the trim won't make the clip invalid
            if new_in >= new_out:
                skipped += 1
                continue

            try:
                await client.timeline.resize_clip(clip.id, new_in, new_out)
                trimmed += 1
            except Exception as e:
                errors.append(f"Clip {clip.id}: {e}")

        return {
            "trimmed": trimmed,
            "skipped": skipped,
            "total_clips": len(clips),
            "errors": errors if errors else None,
        }

    # ==========================================================================
    # Effect Flows
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def flow_add_fade_in_out(
        ctx: Context,
        fade_in_frames: int = 0,
        fade_out_frames: int = 0,
        all_clips: bool = False,
    ) -> dict:
        """Add fade-in and/or fade-out effects to clips using opacity keyframes.

        By default, adds fade-in to the first clip and fade-out to the last clip.
        Set all_clips=True to add fades to every clip.

        Args:
            fade_in_frames: Duration of fade-in in frames (0 to skip)
            fade_out_frames: Duration of fade-out in frames (0 to skip)
            all_clips: If true, apply fades to all clips; otherwise only first/last
        """
        validated = FlowFadeInOutInput(
            fade_in_frames=fade_in_frames,
            fade_out_frames=fade_out_frames,
            all_clips=all_clips,
        )

        if validated.fade_in_frames == 0 and validated.fade_out_frames == 0:
            return {"applied": 0, "message": "No fade durations specified"}

        client = get_client(ctx)
        clips = await client.timeline.get_clips()

        if not clips:
            return {"applied": 0, "message": "No clips on timeline"}

        # Sort by position to find first and last
        sorted_clips = sorted(clips, key=lambda c: c.position)

        applied = 0
        errors: list[str] = []

        async def apply_fade_in(clip) -> bool:
            """Add fade-in keyframes to clip."""
            try:
                # Add opacity effect if needed
                effect_id = await client.effects.add("frei0r.brightness", clip.id)
                # Set keyframes: 0 at start, 1 after fade
                await client.effects.set_keyframe(clip.id, effect_id, "brightness", 0, 0.0)
                await client.effects.set_keyframe(
                    clip.id, effect_id, "brightness", validated.fade_in_frames, 1.0
                )
                return True
            except Exception as e:
                errors.append(f"Fade-in clip {clip.id}: {e}")
                return False

        async def apply_fade_out(clip) -> bool:
            """Add fade-out keyframes to clip."""
            try:
                effect_id = await client.effects.add("frei0r.brightness", clip.id)
                fade_start = clip.duration - validated.fade_out_frames
                await client.effects.set_keyframe(clip.id, effect_id, "brightness", fade_start, 1.0)
                await client.effects.set_keyframe(
                    clip.id, effect_id, "brightness", clip.duration, 0.0
                )
                return True
            except Exception as e:
                errors.append(f"Fade-out clip {clip.id}: {e}")
                return False

        if validated.all_clips:
            for clip in sorted_clips:
                if validated.fade_in_frames > 0 and await apply_fade_in(clip):
                    applied += 1
                if validated.fade_out_frames > 0 and await apply_fade_out(clip):
                    applied += 1
        else:
            # Only first and last
            if validated.fade_in_frames > 0 and await apply_fade_in(sorted_clips[0]):
                applied += 1
            if validated.fade_out_frames > 0 and await apply_fade_out(sorted_clips[-1]):
                applied += 1

        return {
            "applied": applied,
            "total_clips": len(clips),
            "errors": errors if errors else None,
        }

    # ==========================================================================
    # Export Flows
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def flow_export_and_wait(
        ctx: Context,
        preset_name: str,
        output_path: str,
        poll_interval_seconds: float = 2.0,
        timeout_seconds: float = 3600.0,
    ) -> dict:
        """Start a render job and wait for it to complete.

        This flow tool starts a render and polls for completion, returning
        the final status. Useful for synchronous export workflows.

        Args:
            preset_name: Name of the render preset
            output_path: Absolute path for output file
            poll_interval_seconds: How often to check status (default: 2s)
            timeout_seconds: Maximum time to wait (default: 1 hour)
        """
        validated = FlowExportAndWaitInput(
            preset_name=preset_name,
            output_path=output_path,
            poll_interval_seconds=poll_interval_seconds,
            timeout_seconds=timeout_seconds,
        )

        client = get_client(ctx)

        # Start the render
        job = await client.render.start(validated.preset_name, validated.output_path)

        # Poll until complete or timeout
        elapsed = 0.0
        last_progress = 0

        while elapsed < validated.timeout_seconds:
            await asyncio.sleep(validated.poll_interval_seconds)
            elapsed += validated.poll_interval_seconds

            status = await client.render.get_status(job.job_id)

            # Update progress tracking
            if hasattr(status, "progress"):
                last_progress = status.progress

            # Check completion
            if status.status == "completed":
                return {
                    "success": True,
                    "job_id": job.job_id,
                    "output_path": validated.output_path,
                    "elapsed_seconds": elapsed,
                }
            elif status.status == "error":
                return {
                    "success": False,
                    "job_id": job.job_id,
                    "error": getattr(status, "error", "Unknown error"),
                    "elapsed_seconds": elapsed,
                }

        # Timeout
        return {
            "success": False,
            "job_id": job.job_id,
            "error": f"Timeout after {validated.timeout_seconds}s",
            "last_progress": last_progress,
        }

    @mcp.tool()
    @mcp_tool_wrapper
    async def flow_backup_project(
        ctx: Context,
        backup_dir: str,
        include_timestamp: bool = True,
    ) -> dict:
        """Save the project to a timestamped backup location.

        Creates a backup copy of the current project in the specified directory.

        Args:
            backup_dir: Directory to save backup to
            include_timestamp: Whether to add timestamp to filename (default: true)
        """
        import os
        from datetime import datetime

        client = get_client(ctx)

        # Get current project info
        info = await client.project.get_info()

        if not info.path:
            return {"success": False, "error": "Project has not been saved yet"}

        # Generate backup filename
        original_name = os.path.basename(info.path)
        name_part = os.path.splitext(original_name)[0]

        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{name_part}_{timestamp}.kdenlive"
        else:
            backup_name = original_name

        backup_path = os.path.join(backup_dir, backup_name)

        # Save to backup location
        await client.project.save(backup_path)

        return {
            "success": True,
            "backup_path": backup_path,
            "original_path": info.path,
        }

    @mcp.tool()
    @mcp_tool_wrapper
    async def flow_cleanup_unused_clips(ctx: Context) -> dict:
        """Find and delete bin clips that are not used on the timeline.

        Compares clips in the bin with clips on the timeline and removes
        any bin clips that aren't being used.

        WARNING: This operation cannot be undone. Use with caution.
        """
        client = get_client(ctx)

        # Get all bin clips
        bin_clips = await client.bin.list_clips()
        bin_clip_ids = {c.id for c in bin_clips}

        # Get all timeline clips and find which bin clips they reference
        timeline_clips = await client.timeline.get_clips()
        used_bin_ids = {c.bin_id for c in timeline_clips if hasattr(c, "bin_id") and c.bin_id}

        # Find unused
        unused_ids = bin_clip_ids - used_bin_ids

        if not unused_ids:
            return {
                "deleted": 0,
                "message": "All bin clips are in use",
                "total_bin_clips": len(bin_clips),
            }

        # Delete unused clips
        deleted_ids = list(unused_ids)
        count = await client.bin.delete_clips(deleted_ids)

        return {
            "deleted": count,
            "total_bin_clips": len(bin_clips),
            "in_use_clips": len(used_bin_ids),
        }
