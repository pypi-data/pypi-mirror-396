"""MCP tool registration for Kdenlive.

Tools are organized by category for easier maintenance and token-efficient
inspection by AI agents. Each category can be loaded independently if needed.

Categories:
- project: Project management (open, save, close, undo/redo)
- timeline: Timeline operations (clips, tracks, playhead)
- bin: Bin management (clips, folders, markers)
- effects: Effect management (add, remove, properties, keyframes)
- render: Rendering (presets, jobs, status)
- asset: Asset discovery (categories, search, favorites, presets)
- transition: Transitions between clips
- composition: Track compositions/overlays
- utility: Connection and diagnostic tools
- flows: High-level workflow automation tools
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .asset import register_asset_tools
from .bin import register_bin_tools
from .composition import register_composition_tools
from .effects import register_effects_tools
from .flows import register_flow_tools
from .project import register_project_tools
from .render import register_render_tools
from .timeline import register_timeline_tools
from .transition import register_transition_tools
from .utility import register_utility_tools


def register_tools(mcp: FastMCP) -> None:
    """Register all Kdenlive tools with the MCP server.

    This function registers tools from all categories. Each category
    module contains related tools grouped together for easier
    maintenance and documentation.
    """
    # Core operations
    register_project_tools(mcp)
    register_timeline_tools(mcp)
    register_bin_tools(mcp)

    # Effects and assets
    register_effects_tools(mcp)
    register_asset_tools(mcp)

    # Transitions and compositions
    register_transition_tools(mcp)
    register_composition_tools(mcp)

    # Rendering
    register_render_tools(mcp)

    # Utility
    register_utility_tools(mcp)

    # Flow (workflow) tools
    register_flow_tools(mcp)


__all__ = [
    "register_tools",
    "register_project_tools",
    "register_timeline_tools",
    "register_bin_tools",
    "register_effects_tools",
    "register_asset_tools",
    "register_transition_tools",
    "register_composition_tools",
    "register_render_tools",
    "register_utility_tools",
    "register_flow_tools",
]
