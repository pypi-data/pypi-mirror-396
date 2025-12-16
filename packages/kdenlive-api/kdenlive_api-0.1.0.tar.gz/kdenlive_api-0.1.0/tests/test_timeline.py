"""Tests for TimelineAPI."""

from __future__ import annotations

import pytest
from conftest import MockWebSocketServer
from kdenlive_api import KdenliveClient
from kdenlive_api.types import TimelineClip, TimelineInfo, TrackInfo


class TestTimelineGetInfo:
    """Test timeline.get_info method."""

    @pytest.mark.asyncio
    async def test_get_info(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting timeline info."""
        client, server = client_with_server

        info = await client.timeline.get_info()

        assert isinstance(info, TimelineInfo)
        assert info.duration == 7500
        assert info.track_count == 4
        assert info.video_tracks == 2
        assert info.audio_tracks == 2


class TestTimelineGetTracks:
    """Test timeline.get_tracks method."""

    @pytest.mark.asyncio
    async def test_get_tracks(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting tracks."""
        client, server = client_with_server

        tracks = await client.timeline.get_tracks()

        assert len(tracks) == 4
        assert all(isinstance(t, TrackInfo) for t in tracks)
        assert tracks[0].name == "Video 1"
        assert tracks[0].type == "video"
        assert tracks[2].type == "audio"


class TestTimelineGetClips:
    """Test timeline.get_clips method."""

    @pytest.mark.asyncio
    async def test_get_all_clips(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting all clips."""
        client, server = client_with_server

        clips = await client.timeline.get_clips()

        assert len(clips) == 1
        assert isinstance(clips[0], TimelineClip)
        assert clips[0].name == "test_clip.mp4"

    @pytest.mark.asyncio
    async def test_get_clips_by_track(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting clips filtered by track."""
        client, server = client_with_server

        server.register_handler(
            "timeline.getClips",
            lambda params: {"clips": []} if params.get("trackId") == 2 else {"clips": [{"id": 1}]},
        )

        clips = await client.timeline.get_clips(track_id=2)

        assert len(clips) == 0


class TestTimelineGetClip:
    """Test timeline.get_clip method."""

    @pytest.mark.asyncio
    async def test_get_clip(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting single clip."""
        client, server = client_with_server

        server.register_handler(
            "timeline.getClip",
            {
                "id": 1,
                "binId": "clip1",
                "trackId": 1,
                "position": 0,
                "duration": 250,
                "in": 0,
                "out": 250,
                "name": "test_clip.mp4",
            },
        )

        clip = await client.timeline.get_clip(1)

        assert isinstance(clip, TimelineClip)
        assert clip.id == 1


class TestTimelineInsertClip:
    """Test timeline.insert_clip method."""

    @pytest.mark.asyncio
    async def test_insert_clip(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test inserting a clip."""
        client, server = client_with_server

        server.register_handler("timeline.insertClip", {"clipId": 5})

        clip_id = await client.timeline.insert_clip(
            bin_clip_id="clip1",
            track_id=1,
            position=500,
        )

        assert clip_id == 5
        assert server.requests[0]["params"]["binClipId"] == "clip1"
        assert server.requests[0]["params"]["trackId"] == 1
        assert server.requests[0]["params"]["position"] == 500


class TestTimelineMoveClip:
    """Test timeline.move_clip method."""

    @pytest.mark.asyncio
    async def test_move_clip(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test moving a clip."""
        client, server = client_with_server

        server.register_handler("timeline.moveClip", {"moved": True})

        result = await client.timeline.move_clip(1, track_id=2, position=1000)

        assert result is True
        assert server.requests[0]["params"]["clipId"] == 1
        assert server.requests[0]["params"]["trackId"] == 2
        assert server.requests[0]["params"]["position"] == 1000


class TestTimelineDeleteClip:
    """Test timeline.delete_clip method."""

    @pytest.mark.asyncio
    async def test_delete_clip(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test deleting a clip."""
        client, server = client_with_server

        server.register_handler("timeline.deleteClip", {"deleted": True})

        result = await client.timeline.delete_clip(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_clips(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test deleting multiple clips."""
        client, server = client_with_server

        server.register_handler("timeline.deleteClips", {"count": 3})

        result = await client.timeline.delete_clips([1, 2, 3])

        assert result == 3


class TestTimelineResizeClip:
    """Test timeline.resize_clip method."""

    @pytest.mark.asyncio
    async def test_resize_clip(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test resizing a clip."""
        client, server = client_with_server

        server.register_handler("timeline.resizeClip", {"resized": True})

        result = await client.timeline.resize_clip(1, in_point=10, out_point=200)

        assert result is True


class TestTimelineSplitClip:
    """Test timeline.split_clip method."""

    @pytest.mark.asyncio
    async def test_split_clip(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test splitting a clip."""
        client, server = client_with_server

        server.register_handler(
            "timeline.splitClip",
            {"parts": [{"clipId": 1}, {"clipId": 6}]},
        )

        result = await client.timeline.split_clip(1, position=125)

        assert len(result) == 2


class TestTimelineTrackOperations:
    """Test track-related methods."""

    @pytest.mark.asyncio
    async def test_add_track(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test adding a track."""
        client, server = client_with_server

        server.register_handler("timeline.addTrack", {"trackId": 5})

        track_id = await client.timeline.add_track("video", name="VFX")

        assert track_id == 5
        assert server.requests[0]["params"]["type"] == "video"
        assert server.requests[0]["params"]["name"] == "VFX"

    @pytest.mark.asyncio
    async def test_delete_track(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test deleting a track."""
        client, server = client_with_server

        server.register_handler("timeline.deleteTrack", {"deleted": True})

        result = await client.timeline.delete_track(5)

        assert result is True

    @pytest.mark.asyncio
    async def test_set_track_property(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test setting track property."""
        client, server = client_with_server

        server.register_handler("timeline.setTrackProperty", {"updated": True})

        result = await client.timeline.set_track_property(1, "locked", True)

        assert result is True
        assert server.requests[0]["params"]["property"] == "locked"
        assert server.requests[0]["params"]["value"] is True


class TestTimelineNavigation:
    """Test navigation methods."""

    @pytest.mark.asyncio
    async def test_seek(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test seeking."""
        client, server = client_with_server

        server.register_handler("timeline.seek", {"position": 1500})

        position = await client.timeline.seek(1500)

        assert position == 1500

    @pytest.mark.asyncio
    async def test_get_position(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting position."""
        client, server = client_with_server

        server.register_handler("timeline.getPosition", {"position": 1500, "duration": 7500})

        position = await client.timeline.get_position()

        assert position == 1500


class TestTimelineSelection:
    """Test selection methods."""

    @pytest.mark.asyncio
    async def test_get_selection(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting selection."""
        client, server = client_with_server

        server.register_handler("timeline.getSelection", {"clipIds": [1, 2]})

        selection = await client.timeline.get_selection()

        assert selection == [1, 2]

    @pytest.mark.asyncio
    async def test_set_selection(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test setting selection."""
        client, server = client_with_server

        server.register_handler("timeline.setSelection", {"selected": True})

        result = await client.timeline.set_selection([1, 2, 3])

        assert result is True
        assert server.requests[0]["params"]["clipIds"] == [1, 2, 3]
