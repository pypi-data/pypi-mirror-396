"""Effects tools for Kdenlive MCP.

Tools for managing effects, parameters, and keyframes on timeline clips.
"""

from __future__ import annotations

from typing import Any

from kdenlive_api.validators import (
    EffectAddInput,
    EffectCopyToClipsInput,
    EffectEnableDisableInput,
    EffectGetClipEffectsInput,
    EffectGetInfoInput,
    EffectGetPropertyInput,
    EffectKeyframeInput,
    EffectRemoveInput,
    EffectReorderInput,
    EffectSetKeyframeInput,
    EffectSetPropertyInput,
)
from mcp.server.fastmcp import Context, FastMCP

from ._common import get_client, mcp_tool_wrapper


def register_effects_tools(mcp: FastMCP) -> None:
    """Register effects tools."""

    # ==========================================================================
    # Effect Discovery
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

    # ==========================================================================
    # Add/Remove Effects
    # ==========================================================================

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

    # ==========================================================================
    # Effect Properties
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_get_property(
        ctx: Context,
        clip_id: int,
        effect_id: str,
        property_name: str,
    ) -> dict:
        """Get an effect parameter value.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect instance (non-empty string)
            property_name: Name of the property to get (non-empty string)
        """
        validated = EffectGetPropertyInput(
            clip_id=clip_id, effect_id=effect_id, property_name=property_name
        )
        client = get_client(ctx)
        value = await client.effects.get_property(
            validated.clip_id, validated.effect_id, validated.property_name
        )
        return {"value": value}

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

    # ==========================================================================
    # Enable/Disable
    # ==========================================================================

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

    # ==========================================================================
    # Effect Stack Management
    # ==========================================================================

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_reorder(ctx: Context, clip_id: int, effect_id: str, new_index: int) -> dict:
        """Change the order of an effect in the effect stack.

        Effects are applied in order from index 0 upward.

        Args:
            clip_id: ID of the clip (must be >= 0)
            effect_id: ID of the effect to reorder (non-empty string)
            new_index: New position in the effect stack (must be >= 0)
        """
        validated = EffectReorderInput(clip_id=clip_id, effect_id=effect_id, new_index=new_index)
        client = get_client(ctx)
        result = await client.effects.reorder(
            validated.clip_id, validated.effect_id, validated.new_index
        )
        return {"reordered": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def effect_copy_to_clips(
        ctx: Context,
        source_clip_id: int,
        effect_id: str,
        target_clip_ids: list[int],
    ) -> dict:
        """Copy an effect from one clip to multiple other clips.

        This is more efficient than adding and configuring the effect individually.

        Args:
            source_clip_id: ID of the clip with the effect (must be >= 0)
            effect_id: ID of the effect to copy (non-empty string)
            target_clip_ids: List of clip IDs to copy to (at least one, all >= 0)
        """
        validated = EffectCopyToClipsInput(
            source_clip_id=source_clip_id, effect_id=effect_id, target_clip_ids=target_clip_ids
        )
        client = get_client(ctx)
        count = await client.effects.copy_to_clips(
            validated.source_clip_id, validated.effect_id, validated.target_clip_ids
        )
        return {"copied_count": count}

    # ==========================================================================
    # Keyframes
    # ==========================================================================

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
