"""Composition/track overlay API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kdenlive_api.types import CompositionInfo

if TYPE_CHECKING:
    from kdenlive_api.client import KdenliveClient


class CompositionAPI:
    """Composition (track overlay) operations."""

    def __init__(self, client: KdenliveClient) -> None:
        self._client = client

    async def list(self) -> list[CompositionInfo]:
        """List compositions on timeline."""
        result = await self._client.call("composition.list")
        return [CompositionInfo.model_validate(c) for c in result.get("compositions", [])]

    async def add(self, composition_type: str, track: int, position: int) -> CompositionInfo:
        """Add composition to timeline."""
        result = await self._client.call(
            "composition.add",
            {"type": composition_type, "track": track, "position": position},
        )
        return CompositionInfo.model_validate(result)

    async def remove(self, composition_id: int) -> bool:
        """Remove composition."""
        result = await self._client.call("composition.remove", {"compositionId": composition_id})
        return result.get("deleted", False)

    async def get_properties(self, composition_id: int) -> dict[str, Any]:
        """Get composition parameters."""
        result = await self._client.call(
            "composition.getProperties", {"compositionId": composition_id}
        )
        return result

    async def set_property(self, composition_id: int, property_name: str, value: Any) -> bool:
        """Set composition parameter."""
        result = await self._client.call(
            "composition.setProperty",
            {"compositionId": composition_id, "property": property_name, "value": value},
        )
        return result.get("updated", False)
