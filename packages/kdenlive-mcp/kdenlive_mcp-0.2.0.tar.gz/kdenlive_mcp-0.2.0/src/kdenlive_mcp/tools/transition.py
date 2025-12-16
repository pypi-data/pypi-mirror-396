"""Transition tools for Kdenlive MCP.

Tools for managing transitions between clips.
"""

from __future__ import annotations

from typing import Any

from kdenlive_api.validators import (
    TransitionAddInput,
    TransitionRemoveInput,
    TransitionSetPropertyInput,
)
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from ._common import get_client, mcp_tool_wrapper


class TransitionGetPropertiesInput(BaseModel):
    """Validate transition.getProperties parameters."""

    transition_id: int = Field(ge=0, description="Transition ID")


def register_transition_tools(mcp: FastMCP) -> None:
    """Register transition tools."""

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

    @mcp.tool()
    @mcp_tool_wrapper
    async def transition_get_properties(ctx: Context, transition_id: int) -> dict:
        """Get all properties/parameters of a transition.

        Args:
            transition_id: ID of the transition (must be >= 0)
        """
        validated = TransitionGetPropertiesInput(transition_id=transition_id)
        client = get_client(ctx)
        properties = await client.transition.get_properties(validated.transition_id)
        return {"properties": properties}

    @mcp.tool()
    @mcp_tool_wrapper
    async def transition_set_property(
        ctx: Context,
        transition_id: int,
        property_name: str,
        value: Any,
    ) -> dict:
        """Set a transition property/parameter.

        Args:
            transition_id: ID of the transition (must be >= 0)
            property_name: Name of the property to set (non-empty string)
            value: New value for the property
        """
        validated = TransitionSetPropertyInput(
            transition_id=transition_id, property_name=property_name, value=value
        )
        client = get_client(ctx)
        result = await client.transition.set_property(
            validated.transition_id, validated.property_name, validated.value
        )
        return {"updated": result}
