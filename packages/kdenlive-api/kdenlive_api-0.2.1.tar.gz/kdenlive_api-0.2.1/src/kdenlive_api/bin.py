"""Bin/clip management API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kdenlive_api.types import ClipInfo, FolderInfo, Marker

if TYPE_CHECKING:
    from kdenlive_api.client import KdenliveClient


class BinAPI:
    """Bin/clip management operations."""

    def __init__(self, client: KdenliveClient) -> None:
        self._client = client

    async def list_clips(self, folder_id: str | None = None) -> list[ClipInfo]:
        """List clips in bin."""
        params = {"folderId": folder_id} if folder_id else {}
        result = await self._client.call("bin.listClips", params)
        # Server may return list directly or wrapped in {"clips": [...]}
        clips = result if isinstance(result, list) else result.get("clips", [])
        return [ClipInfo.model_validate(c) for c in clips]

    async def list_folders(self) -> list[FolderInfo]:
        """List folders in bin."""
        result = await self._client.call("bin.listFolders")
        # Server may return list directly or wrapped in {"folders": [...]}
        folders = result if isinstance(result, list) else result.get("folders", [])
        return [FolderInfo.model_validate(f) for f in folders]

    async def get_clip_info(self, clip_id: str) -> ClipInfo:
        """Get detailed clip information."""
        result = await self._client.call("bin.getClipInfo", {"clipId": clip_id})
        return ClipInfo.model_validate(result)

    async def import_clip(
        self,
        url: str,
        folder_id: str | None = None,
        server_timeout: int | None = None,
    ) -> str:
        """Import single media file. Returns clip ID.

        Args:
            url: Path to the media file to import.
            folder_id: Optional folder ID to import into.
            server_timeout: Server-side timeout in milliseconds.
                - None (default): Use server default (10s)
                - 0: Return immediately (non-blocking, poll with get_clip_info)
                - >0: Wait up to this many ms for import to complete

        Returns:
            The clip ID of the imported clip.
        """
        params: dict[str, str | int] = {"url": url}
        if folder_id:
            params["folderId"] = folder_id
        if server_timeout is not None:
            params["timeout"] = server_timeout
        result = await self._client.call("bin.importClip", params)
        return result.get("clipId", "")

    async def import_clips(
        self,
        urls: list[str],
        folder_id: str | None = None,
        server_timeout: int | None = None,
    ) -> list[str]:
        """Import multiple media files. Returns clip IDs.

        Args:
            urls: List of paths to media files to import.
            folder_id: Optional folder ID to import into.
            server_timeout: Server-side timeout in milliseconds (per clip).
                - None (default): Use server default (10s)
                - 0: Return immediately (non-blocking, poll with get_clip_info)
                - >0: Wait up to this many ms for each import to complete

        Returns:
            List of clip IDs for the imported clips.
        """
        params: dict[str, str | int | list[str]] = {"urls": urls}
        if folder_id:
            params["folderId"] = folder_id
        if server_timeout is not None:
            params["timeout"] = server_timeout
        result = await self._client.call("bin.importClips", params)
        return result.get("clipIds", [])

    async def delete_clip(self, clip_id: str) -> bool:
        """Delete single clip from bin."""
        result = await self._client.call("bin.deleteClip", {"clipId": clip_id})
        return result.get("deleted", False)

    async def delete_clips(self, clip_ids: list[str]) -> int:
        """Delete multiple clips from bin. Returns count deleted."""
        result = await self._client.call("bin.deleteClips", {"clipIds": clip_ids})
        return result.get("count", 0)

    async def rename_item(self, item_id: str, name: str) -> bool:
        """Rename clip or folder."""
        result = await self._client.call("bin.renameItem", {"itemId": item_id, "name": name})
        return result.get("renamed", False)

    async def move_item(self, item_id: str, target_folder_id: str) -> bool:
        """Move clip or folder to different folder."""
        result = await self._client.call(
            "bin.moveItem", {"itemId": item_id, "folderId": target_folder_id}
        )
        return result.get("moved", False)

    async def create_folder(self, name: str, parent_id: str | None = None) -> str:
        """Create folder in bin. Returns folder ID."""
        params: dict[str, str] = {"name": name}
        if parent_id:
            params["parentId"] = parent_id
        result = await self._client.call("bin.createFolder", params)
        return result["folderId"]

    async def delete_folder(self, folder_id: str) -> bool:
        """Delete folder from bin."""
        result = await self._client.call("bin.deleteFolder", {"folderId": folder_id})
        return result.get("deleted", False)

    async def get_clip_markers(self, clip_id: str) -> list[Marker]:
        """Get markers on a clip."""
        result = await self._client.call("bin.getClipMarkers", {"clipId": clip_id})
        return [Marker.model_validate(m) for m in result.get("markers", [])]

    async def add_clip_marker(self, clip_id: str, position: int, comment: str = "") -> int:
        """Add marker to clip. Returns marker ID."""
        result = await self._client.call(
            "bin.addClipMarker",
            {"clipId": clip_id, "position": position, "comment": comment},
        )
        return result["markerId"]

    async def delete_clip_marker(self, clip_id: str, marker_id: int) -> bool:
        """Delete marker from clip."""
        result = await self._client.call(
            "bin.deleteClipMarker", {"clipId": clip_id, "markerId": marker_id}
        )
        return result.get("deleted", False)
