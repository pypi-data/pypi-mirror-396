"""Render tools for Kdenlive MCP.

Tools for rendering projects to video files.
"""

from __future__ import annotations

from kdenlive_api.validators import (
    RenderGetPresetInfoInput,
    RenderGetStatusInput,
    RenderStartInput,
    RenderStartWithGuidesInput,
    RenderStopInput,
)
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from ._common import get_client, mcp_tool_wrapper


class RenderSetOutputInput(BaseModel):
    """Validate render.setOutput parameters."""

    default_path: str = Field(min_length=1, description="Default output path")


def register_render_tools(mcp: FastMCP) -> None:
    """Register render tools."""

    # ==========================================================================
    # Presets
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
    async def render_get_preset_info(ctx: Context, preset_name: str) -> dict:
        """Get detailed information about a render preset.

        Args:
            preset_name: Name of the preset to inspect (non-empty string)
        """
        validated = RenderGetPresetInfoInput(preset_name=preset_name)
        client = get_client(ctx)
        info = await client.render.get_preset_info(validated.preset_name)
        return info.model_dump()

    # ==========================================================================
    # Start Render
    # ==========================================================================

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
    async def render_start_with_guides(
        ctx: Context,
        preset_name: str,
        output_dir: str,
    ) -> list[dict]:
        """Start render jobs for segments between guide markers.

        This is useful for chapter-based export where each guide-delimited
        section becomes a separate output file.

        Args:
            preset_name: Name of the render preset to use (non-empty string)
            output_dir: Absolute path to output directory
        """
        validated = RenderStartWithGuidesInput(preset_name=preset_name, output_dir=output_dir)
        client = get_client(ctx)
        jobs = await client.render.start_with_guides(validated.preset_name, validated.output_dir)
        return [j.model_dump() for j in jobs]

    # ==========================================================================
    # Job Management
    # ==========================================================================

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
    async def render_stop_all(ctx: Context) -> dict:
        """Stop all active render jobs.

        Returns the count of jobs that were stopped.
        """
        client = get_client(ctx)
        count = await client.render.stop_all()
        return {"stopped_count": count}

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
    # Configuration
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def render_set_output(ctx: Context, default_path: str) -> dict:
        """Set the default output path for renders.

        Args:
            default_path: Default output path (non-empty string)
        """
        validated = RenderSetOutputInput(default_path=default_path)
        client = get_client(ctx)
        result = await client.render.set_output(validated.default_path)
        return {"set": result}
