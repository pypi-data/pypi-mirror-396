"""Timeline operations API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from kdenlive_api.types import TimelineClip, TimelineInfo, TrackInfo

if TYPE_CHECKING:
    from kdenlive_api.client import KdenliveClient


class TimelineAPI:
    """Timeline operations."""

    def __init__(self, client: KdenliveClient) -> None:
        self._client = client

    async def get_info(self) -> TimelineInfo:
        """Get timeline information."""
        result = await self._client.call("timeline.getInfo")
        return TimelineInfo.model_validate(result)

    async def get_tracks(self) -> list[TrackInfo]:
        """Get all tracks."""
        result = await self._client.call("timeline.getTracks")
        # Server may return list directly or wrapped in {"tracks": [...]}
        tracks = result if isinstance(result, list) else result.get("tracks", [])
        return [TrackInfo.model_validate(t) for t in tracks]

    async def get_clips(self, track_id: int | None = None) -> list[TimelineClip]:
        """Get clips on timeline."""
        params = {"trackId": track_id} if track_id is not None else {}
        result = await self._client.call("timeline.getClips", params)
        # Server may return list directly or wrapped in {"clips": [...]}
        clips = result if isinstance(result, list) else result.get("clips", [])
        return [TimelineClip.model_validate(c) for c in clips]

    async def get_clip(self, clip_id: int) -> TimelineClip:
        """Get single clip info by ID."""
        result = await self._client.call("timeline.getClip", {"clipId": clip_id})
        return TimelineClip.model_validate(result)

    async def get_position(self) -> int:
        """Get current playhead position."""
        result = await self._client.call("timeline.getPosition")
        return result.get("position", 0)

    async def get_selection(self) -> list[int]:
        """Get IDs of currently selected clips."""
        result = await self._client.call("timeline.getSelection")
        return result.get("clipIds", [])

    async def insert_clip(
        self,
        bin_clip_id: str,
        track_id: int,
        position: int,
    ) -> int:
        """Insert bin clip to timeline. Returns clip ID."""
        params: dict[str, Any] = {
            "binId": bin_clip_id,  # Server expects "binId" not "binClipId"
            "trackId": track_id,
            "position": position,
        }
        result = await self._client.call("timeline.insertClip", params)
        return result.get("clipId", result.get("id", 0))

    async def move_clip(self, clip_id: int, track_id: int, position: int) -> bool:
        """Move clip to new track/position."""
        params: dict[str, Any] = {
            "clipId": clip_id,
            "trackId": track_id,
            "position": position,
        }
        result = await self._client.call("timeline.moveClip", params)
        return result.get("moved", False)

    async def delete_clip(self, clip_id: int) -> bool:
        """Delete single clip from timeline."""
        result = await self._client.call("timeline.deleteClip", {"clipId": clip_id})
        return result.get("deleted", False)

    async def delete_clips(self, clip_ids: list[int]) -> int:
        """Delete multiple clips from timeline. Returns count deleted."""
        result = await self._client.call("timeline.deleteClips", {"clipIds": clip_ids})
        return result.get("count", 0)

    async def resize_clip(self, clip_id: int, in_point: int, out_point: int) -> bool:
        """Change clip in/out points."""
        result = await self._client.call(
            "timeline.resizeClip",
            {"clipId": clip_id, "in": in_point, "out": out_point},
        )
        return result.get("resized", False)

    async def split_clip(self, clip_id: int, position: int) -> list[dict[str, Any]]:
        """Split clip at position. Returns info about resulting parts."""
        result = await self._client.call(
            "timeline.splitClip", {"clipId": clip_id, "position": position}
        )
        return result.get("parts", [])

    async def add_track(
        self,
        track_type: Literal["video", "audio"],
        name: str | None = None,
    ) -> int:
        """Add new track. Returns track ID."""
        params: dict[str, Any] = {"type": track_type}
        if name is not None:
            params["name"] = name
        result = await self._client.call("timeline.addTrack", params)
        return result["trackId"]

    async def delete_track(self, track_id: int) -> bool:
        """Delete track."""
        result = await self._client.call("timeline.deleteTrack", {"trackId": track_id})
        return result.get("deleted", False)

    async def set_track_property(
        self,
        track_id: int,
        property_name: Literal["name", "locked", "muted", "hidden"],
        value: str | bool,
    ) -> bool:
        """Set track property (name, locked, muted, hidden)."""
        result = await self._client.call(
            "timeline.setTrackProperty",
            {"trackId": track_id, "property": property_name, "value": value},
        )
        return result.get("updated", True) if result else True

    async def seek(self, position: int) -> int:
        """Seek playhead to position."""
        result = await self._client.call("timeline.seek", {"position": position})
        return result.get("position", position)

    async def set_selection(self, clip_ids: list[int]) -> bool:
        """Select specific clips."""
        await self._client.call("timeline.setSelection", {"clipIds": clip_ids})
        # Server returns count of selected items - if call succeeded, selection was set
        return True
