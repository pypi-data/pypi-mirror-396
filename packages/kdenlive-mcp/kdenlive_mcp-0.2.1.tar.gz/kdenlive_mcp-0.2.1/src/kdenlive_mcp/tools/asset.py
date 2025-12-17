"""Asset discovery tools for Kdenlive MCP.

Tools for browsing and managing effects, transitions, and presets.
"""

from __future__ import annotations

from kdenlive_api.validators import (
    AssetDeletePresetInput,
    AssetFavoriteInput,
    AssetGetEffectsByCategoryInput,
    AssetGetPresetsInput,
    AssetSavePresetInput,
    AssetSearchInput,
)
from mcp.server.fastmcp import Context, FastMCP

from ._common import get_client, mcp_tool_wrapper


def register_asset_tools(mcp: FastMCP) -> None:
    """Register asset discovery tools."""

    # ==========================================================================
    # Discovery
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

    # ==========================================================================
    # Favorites
    # ==========================================================================

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

    # ==========================================================================
    # Presets
    # ==========================================================================

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
    async def asset_save_preset(ctx: Context, effect_id: str, preset_name: str) -> dict:
        """Save effect settings as a preset.

        Args:
            effect_id: ID of the effect (non-empty string)
            preset_name: Name for the preset (non-empty string)
        """
        validated = AssetSavePresetInput(effect_id=effect_id, preset_name=preset_name)
        client = get_client(ctx)
        result = await client.asset.save_preset(validated.effect_id, validated.preset_name)
        return {"saved": result}

    @mcp.tool()
    @mcp_tool_wrapper
    async def asset_delete_preset(ctx: Context, effect_id: str, preset_name: str) -> dict:
        """Delete a saved effect preset.

        Args:
            effect_id: ID of the effect (non-empty string)
            preset_name: Name of the preset to delete (non-empty string)
        """
        validated = AssetDeletePresetInput(effect_id=effect_id, preset_name=preset_name)
        client = get_client(ctx)
        result = await client.asset.delete_preset(validated.effect_id, validated.preset_name)
        return {"deleted": result}
