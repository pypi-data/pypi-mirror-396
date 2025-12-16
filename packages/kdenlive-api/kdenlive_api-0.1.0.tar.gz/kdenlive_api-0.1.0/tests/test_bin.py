"""Tests for BinAPI."""

from __future__ import annotations

import pytest
from conftest import MockWebSocketServer
from kdenlive_api import KdenliveClient
from kdenlive_api.types import ClipInfo, FolderInfo, Marker


class TestBinListClips:
    """Test bin.list_clips method."""

    @pytest.mark.asyncio
    async def test_list_clips_empty(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test listing clips when empty."""
        client, server = client_with_server

        clips = await client.bin.list_clips()

        assert clips == []

    @pytest.mark.asyncio
    async def test_list_clips(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test listing clips."""
        client, server = client_with_server

        server.register_handler(
            "bin.listClips",
            {
                "clips": [
                    {
                        "id": "1",
                        "name": "video1.mp4",
                        "type": "video",
                        "duration": 5000,
                        "url": "/path/to/video1.mp4",
                        "hasAudio": True,
                        "hasVideo": True,
                        "width": 1920,
                        "height": 1080,
                    }
                ]
            },
        )

        clips = await client.bin.list_clips()

        assert len(clips) == 1
        assert isinstance(clips[0], ClipInfo)
        assert clips[0].name == "video1.mp4"

    @pytest.mark.asyncio
    async def test_list_clips_by_folder(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test listing clips in folder."""
        client, server = client_with_server

        server.register_handler("bin.listClips", {"clips": []})

        _clips = await client.bin.list_clips(folder_id="folder1")

        assert server.requests[0]["params"]["folderId"] == "folder1"


class TestBinListFolders:
    """Test bin.list_folders method."""

    @pytest.mark.asyncio
    async def test_list_folders(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test listing folders."""
        client, server = client_with_server

        server.register_handler(
            "bin.listFolders",
            {
                "folders": [
                    {"id": "folder1", "name": "Raw Footage", "parentId": None},
                    {"id": "folder2", "name": "B-Roll", "parentId": "folder1"},
                ]
            },
        )

        folders = await client.bin.list_folders()

        assert len(folders) == 2
        assert isinstance(folders[0], FolderInfo)
        assert folders[0].name == "Raw Footage"
        assert folders[1].parent_id == "folder1"


class TestBinGetClipInfo:
    """Test bin.get_clip_info method."""

    @pytest.mark.asyncio
    async def test_get_clip_info(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting clip info."""
        client, server = client_with_server

        server.register_handler(
            "bin.getClipInfo",
            {
                "id": "2",
                "name": "video1.mp4",
                "type": "video",
                "duration": 5000,
                "url": "/path/to/video1.mp4",
                "hasAudio": True,
                "hasVideo": True,
                "width": 1920,
                "height": 1080,
            },
        )

        info = await client.bin.get_clip_info("2")

        assert isinstance(info, ClipInfo)
        assert info.id == "2"


class TestBinImport:
    """Test bin import methods."""

    @pytest.mark.asyncio
    async def test_import_clip(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test importing single clip."""
        client, server = client_with_server

        server.register_handler("bin.importClip", {"clipId": "5"})

        clip_id = await client.bin.import_clip("/path/to/video.mp4")

        assert clip_id == "5"
        assert server.requests[0]["params"]["url"] == "/path/to/video.mp4"

    @pytest.mark.asyncio
    async def test_import_clip_to_folder(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test importing clip to folder."""
        client, server = client_with_server

        server.register_handler("bin.importClip", {"clipId": "5"})

        _clip_id = await client.bin.import_clip("/path/to/video.mp4", folder_id="folder1")

        assert server.requests[0]["params"]["folderId"] == "folder1"

    @pytest.mark.asyncio
    async def test_import_clips(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test importing multiple clips."""
        client, server = client_with_server

        server.register_handler("bin.importClips", {"clipIds": ["5", "6"]})

        clip_ids = await client.bin.import_clips(
            [
                "/path/to/video1.mp4",
                "/path/to/video2.mp4",
            ]
        )

        assert clip_ids == ["5", "6"]


class TestBinDelete:
    """Test bin delete methods."""

    @pytest.mark.asyncio
    async def test_delete_clip(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test deleting clip."""
        client, server = client_with_server

        server.register_handler("bin.deleteClip", {"deleted": True})

        result = await client.bin.delete_clip("2")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_clips(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test deleting multiple clips."""
        client, server = client_with_server

        server.register_handler("bin.deleteClips", {"count": 3})

        result = await client.bin.delete_clips(["1", "2", "3"])

        assert result == 3


class TestBinOrganize:
    """Test bin organization methods."""

    @pytest.mark.asyncio
    async def test_rename_item(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test renaming item."""
        client, server = client_with_server

        server.register_handler("bin.renameItem", {"renamed": True})

        result = await client.bin.rename_item("2", "New Name")

        assert result is True
        assert server.requests[0]["params"]["name"] == "New Name"

    @pytest.mark.asyncio
    async def test_move_item(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test moving item to folder."""
        client, server = client_with_server

        server.register_handler("bin.moveItem", {"moved": True})

        result = await client.bin.move_item("2", "folder1")

        assert result is True
        assert server.requests[0]["params"]["targetFolderId"] == "folder1"

    @pytest.mark.asyncio
    async def test_create_folder(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test creating folder."""
        client, server = client_with_server

        server.register_handler("bin.createFolder", {"folderId": "folder3"})

        folder_id = await client.bin.create_folder("New Folder", parent_id="folder1")

        assert folder_id == "folder3"
        assert server.requests[0]["params"]["name"] == "New Folder"
        assert server.requests[0]["params"]["parentId"] == "folder1"

    @pytest.mark.asyncio
    async def test_delete_folder(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test deleting folder."""
        client, server = client_with_server

        server.register_handler("bin.deleteFolder", {"deleted": True})

        result = await client.bin.delete_folder("folder1")

        assert result is True


class TestBinMarkers:
    """Test bin marker methods."""

    @pytest.mark.asyncio
    async def test_get_clip_markers(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting clip markers."""
        client, server = client_with_server

        server.register_handler(
            "bin.getClipMarkers",
            {"markers": [{"id": 1, "position": 100, "comment": "Good take", "type": 0}]},
        )

        markers = await client.bin.get_clip_markers("2")

        assert len(markers) == 1
        assert isinstance(markers[0], Marker)
        assert markers[0].comment == "Good take"

    @pytest.mark.asyncio
    async def test_add_clip_marker(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test adding marker."""
        client, server = client_with_server

        server.register_handler("bin.addClipMarker", {"markerId": 2})

        marker_id = await client.bin.add_clip_marker("2", 250, "Start here")

        assert marker_id == 2
        assert server.requests[0]["params"]["position"] == 250
        assert server.requests[0]["params"]["comment"] == "Start here"

    @pytest.mark.asyncio
    async def test_delete_clip_marker(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test deleting marker."""
        client, server = client_with_server

        server.register_handler("bin.deleteClipMarker", {"deleted": True})

        result = await client.bin.delete_clip_marker("2", 1)

        assert result is True
