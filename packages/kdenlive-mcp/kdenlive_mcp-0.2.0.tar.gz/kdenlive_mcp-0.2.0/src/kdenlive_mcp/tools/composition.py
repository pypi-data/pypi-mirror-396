"""Composition tools for Kdenlive MCP.

Tools for managing track compositions/overlays.
"""

from __future__ import annotations

from typing import Any

from kdenlive_api.validators import (
    CompositionAddInput,
    CompositionRemoveInput,
    CompositionSetPropertyInput,
)
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from ._common import get_client, mcp_tool_wrapper


class CompositionGetPropertiesInput(BaseModel):
    """Validate composition.getProperties parameters."""

    composition_id: int = Field(ge=0, description="Composition ID")


def register_composition_tools(mcp: FastMCP) -> None:
    """Register composition tools."""

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

    @mcp.tool()
    @mcp_tool_wrapper
    async def composition_get_properties(ctx: Context, composition_id: int) -> dict:
        """Get all properties/parameters of a composition.

        Args:
            composition_id: ID of the composition (must be >= 0)
        """
        validated = CompositionGetPropertiesInput(composition_id=composition_id)
        client = get_client(ctx)
        properties = await client.composition.get_properties(validated.composition_id)
        return {"properties": properties}

    @mcp.tool()
    @mcp_tool_wrapper
    async def composition_set_property(
        ctx: Context,
        composition_id: int,
        property_name: str,
        value: Any,
    ) -> dict:
        """Set a composition property/parameter.

        Args:
            composition_id: ID of the composition (must be >= 0)
            property_name: Name of the property to set (non-empty string)
            value: New value for the property
        """
        validated = CompositionSetPropertyInput(
            composition_id=composition_id, property_name=property_name, value=value
        )
        client = get_client(ctx)
        result = await client.composition.set_property(
            validated.composition_id, validated.property_name, validated.value
        )
        return {"updated": result}
