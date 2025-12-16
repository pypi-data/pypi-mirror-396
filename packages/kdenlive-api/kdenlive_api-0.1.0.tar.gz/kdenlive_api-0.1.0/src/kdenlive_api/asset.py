"""Asset/library discovery API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kdenlive_api.types import (
    AssetCategory,
    AssetSearchResult,
    EffectInfo,
    EffectPreset,
    FavoriteAsset,
)

if TYPE_CHECKING:
    from kdenlive_api.client import KdenliveClient


class AssetAPI:
    """Asset discovery and management operations."""

    def __init__(self, client: KdenliveClient) -> None:
        self._client = client

    async def list_categories(self) -> list[AssetCategory]:
        """List effect/transition categories."""
        result = await self._client.call("asset.listCategories")
        return [AssetCategory.model_validate(c) for c in result.get("categories", [])]

    async def search(self, query: str) -> list[AssetSearchResult]:
        """Search assets by name/description."""
        result = await self._client.call("asset.search", {"query": query})
        return [AssetSearchResult.model_validate(r) for r in result.get("results", [])]

    async def get_effects_by_category(self, category: str) -> list[EffectInfo]:
        """Get effects in a category."""
        result = await self._client.call("asset.getEffectsByCategory", {"category": category})
        return [EffectInfo.model_validate(e) for e in result.get("effects", [])]

    async def get_favorites(self) -> list[FavoriteAsset]:
        """Get user favorite assets."""
        result = await self._client.call("asset.getFavorites")
        return [FavoriteAsset.model_validate(f) for f in result.get("favorites", [])]

    async def add_favorite(self, asset_id: str) -> bool:
        """Add asset to favorites."""
        result = await self._client.call("asset.addFavorite", {"assetId": asset_id})
        return result.get("added", False)

    async def remove_favorite(self, asset_id: str) -> bool:
        """Remove asset from favorites."""
        result = await self._client.call("asset.removeFavorite", {"assetId": asset_id})
        return result.get("removed", False)

    async def get_presets(self, effect_id: str) -> list[EffectPreset]:
        """Get presets for an effect."""
        result = await self._client.call("asset.getPresets", {"effectId": effect_id})
        return [EffectPreset.model_validate(p) for p in result.get("presets", [])]

    async def save_preset(self, effect_id: str, preset_name: str) -> bool:
        """Save effect preset."""
        result = await self._client.call(
            "asset.savePreset", {"effectId": effect_id, "presetName": preset_name}
        )
        return result.get("saved", False)

    async def delete_preset(self, effect_id: str, preset_name: str) -> bool:
        """Delete effect preset."""
        result = await self._client.call(
            "asset.deletePreset", {"effectId": effect_id, "presetName": preset_name}
        )
        return result.get("deleted", False)
