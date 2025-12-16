"""Transition API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kdenlive_api.types import TransitionInfo, TransitionType

if TYPE_CHECKING:
    from kdenlive_api.client import KdenliveClient


class TransitionAPI:
    """Transition operations."""

    def __init__(self, client: KdenliveClient) -> None:
        self._client = client

    async def list(self) -> list[TransitionType]:
        """List available transition types."""
        result = await self._client.call("transition.list")
        return [TransitionType.model_validate(t) for t in result.get("transitions", [])]

    async def add(self, transition_type: str, from_clip_id: int, to_clip_id: int) -> TransitionInfo:
        """Add transition between clips."""
        result = await self._client.call(
            "transition.add",
            {"type": transition_type, "fromClipId": from_clip_id, "toClipId": to_clip_id},
        )
        return TransitionInfo.model_validate(result)

    async def remove(self, transition_id: int) -> bool:
        """Remove transition."""
        result = await self._client.call("transition.remove", {"transitionId": transition_id})
        return result.get("deleted", False)

    async def get_properties(self, transition_id: int) -> dict[str, Any]:
        """Get transition parameters."""
        result = await self._client.call(
            "transition.getProperties", {"transitionId": transition_id}
        )
        return result

    async def set_property(self, transition_id: int, property_name: str, value: Any) -> bool:
        """Set transition parameter."""
        result = await self._client.call(
            "transition.setProperty",
            {"transitionId": transition_id, "property": property_name, "value": value},
        )
        return result.get("updated", False)
