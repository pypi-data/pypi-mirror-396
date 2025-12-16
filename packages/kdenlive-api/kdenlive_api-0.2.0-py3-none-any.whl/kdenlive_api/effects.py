"""Effects API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kdenlive_api.types import ClipEffect, EffectDetailedInfo, EffectInfo, Keyframe

if TYPE_CHECKING:
    from kdenlive_api.client import KdenliveClient


class EffectsAPI:
    """Effect operations."""

    def __init__(self, client: KdenliveClient) -> None:
        self._client = client

    async def list_available(self) -> list[EffectInfo]:
        """List all available effects."""
        result = await self._client.call("effect.listAvailable")
        # Server may return list directly or wrapped in {"effects": [...]}
        effects = result if isinstance(result, list) else result.get("effects", [])
        return [EffectInfo.model_validate(e) for e in effects]

    async def get_info(self, effect_id: str) -> EffectDetailedInfo:
        """Get effect details with parameter definitions."""
        result = await self._client.call("effect.getInfo", {"effectId": effect_id})
        return EffectDetailedInfo.model_validate(result)

    async def add(self, effect_id: str, clip_id: int) -> str:
        """Add effect to clip. Returns effect instance ID or effect ID if not provided."""
        result = await self._client.call("effect.add", {"effectId": effect_id, "clipId": clip_id})
        # Server may return effectInstanceId, or just indicate success
        return result.get("effectInstanceId", effect_id)

    async def remove(self, clip_id: int, effect_id: str) -> bool:
        """Remove effect from clip."""
        result = await self._client.call(
            "effect.remove", {"clipId": clip_id, "effectId": effect_id}
        )
        return result.get("deleted", False)

    async def get_clip_effects(self, clip_id: int) -> list[ClipEffect]:
        """List effects on clip."""
        result = await self._client.call("effect.getClipEffects", {"clipId": clip_id})
        # Server may return list directly or wrapped in {"effects": [...]}
        effects = result if isinstance(result, list) else result.get("effects", [])
        return [ClipEffect.model_validate(e) for e in effects]

    async def get_property(self, clip_id: int, effect_id: str, property_name: str) -> Any:
        """Get effect parameter value."""
        result = await self._client.call(
            "effect.getProperty",
            {"clipId": clip_id, "effectId": effect_id, "property": property_name},
        )
        return result.get("value")

    async def set_property(
        self, clip_id: int, effect_id: str, property_name: str, value: Any
    ) -> bool:
        """Set effect parameter value."""
        result = await self._client.call(
            "effect.setProperty",
            {
                "clipId": clip_id,
                "effectId": effect_id,
                "property": property_name,
                "value": value,
            },
        )
        return result.get("updated", False)

    async def enable(self, clip_id: int, effect_id: str) -> bool:
        """Enable effect."""
        result = await self._client.call(
            "effect.enable", {"clipId": clip_id, "effectId": effect_id}
        )
        return result.get("enabled", False)

    async def disable(self, clip_id: int, effect_id: str) -> bool:
        """Disable effect."""
        result = await self._client.call(
            "effect.disable", {"clipId": clip_id, "effectId": effect_id}
        )
        return not result.get("enabled", True)

    async def reorder(self, clip_id: int, effect_id: str, new_index: int) -> bool:
        """Change effect order in stack."""
        result = await self._client.call(
            "effect.reorder",
            {"clipId": clip_id, "effectId": effect_id, "newIndex": new_index},
        )
        return result.get("reordered", False)

    async def copy_to_clips(
        self, source_clip_id: int, effect_id: str, target_clip_ids: list[int]
    ) -> int:
        """Copy effect to multiple clips. Returns count of copies made."""
        result = await self._client.call(
            "effect.copyToClips",
            {
                "sourceClipId": source_clip_id,
                "effectId": effect_id,
                "targetClipIds": target_clip_ids,
            },
        )
        return result.get("count", 0)

    async def get_keyframes(
        self, clip_id: int, effect_id: str, property_name: str
    ) -> list[Keyframe]:
        """Get keyframe data for effect property."""
        result = await self._client.call(
            "effect.getKeyframes",
            {"clipId": clip_id, "effectId": effect_id, "property": property_name},
        )
        return [Keyframe.model_validate(k) for k in result.get("keyframes", [])]

    async def set_keyframe(
        self,
        clip_id: int,
        effect_id: str,
        property_name: str,
        position: int,
        value: Any,
    ) -> bool:
        """Add or modify keyframe."""
        result = await self._client.call(
            "effect.setKeyframe",
            {
                "clipId": clip_id,
                "effectId": effect_id,
                "property": property_name,
                "position": position,
                "value": value,
            },
        )
        return result.get("set", False)

    async def delete_keyframe(
        self, clip_id: int, effect_id: str, property_name: str, position: int
    ) -> bool:
        """Remove keyframe."""
        result = await self._client.call(
            "effect.deleteKeyframe",
            {
                "clipId": clip_id,
                "effectId": effect_id,
                "property": property_name,
                "position": position,
            },
        )
        return result.get("deleted", False)
