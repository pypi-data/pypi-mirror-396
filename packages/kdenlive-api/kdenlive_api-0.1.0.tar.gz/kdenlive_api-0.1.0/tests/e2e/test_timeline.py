"""E2E tests for timeline operations."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import skip_without_sample_video
from kdenlive_api import KdenliveClient
from kdenlive_api.types import TimelineClip, TimelineInfo, TrackInfo


@pytest.mark.integration
class TestTimelineInfo:
    """Test timeline info operations."""

    @pytest.mark.asyncio
    async def test_get_timeline_info(self, client_with_empty_project: KdenliveClient) -> None:
        """Test getting timeline info."""
        info = await client_with_empty_project.timeline.get_info()

        assert isinstance(info, TimelineInfo)
        assert info.duration >= 0
        assert info.track_count >= 0
        assert info.position >= 0


@pytest.mark.integration
class TestTrackOperations:
    """Test track management operations."""

    @pytest.mark.asyncio
    async def test_get_tracks(self, client_with_empty_project: KdenliveClient) -> None:
        """Test getting all tracks."""
        tracks = await client_with_empty_project.timeline.get_tracks()

        assert isinstance(tracks, list)
        # New project should have some default tracks
        for track in tracks:
            assert isinstance(track, TrackInfo)
            assert track.type in ("video", "audio")

    @pytest.mark.asyncio
    async def test_add_video_track(self, client_with_empty_project: KdenliveClient) -> None:
        """Test adding a video track."""
        client = client_with_empty_project

        tracks_before = await client.timeline.get_tracks()
        video_count_before = sum(1 for t in tracks_before if t.type == "video")

        track_id = await client.timeline.add_track("video", name="My Video Track")
        assert isinstance(track_id, int)
        assert track_id > 0

        tracks_after = await client.timeline.get_tracks()
        video_count_after = sum(1 for t in tracks_after if t.type == "video")
        assert video_count_after == video_count_before + 1

    @pytest.mark.asyncio
    async def test_add_audio_track(self, client_with_empty_project: KdenliveClient) -> None:
        """Test adding an audio track."""
        client = client_with_empty_project

        tracks_before = await client.timeline.get_tracks()
        audio_count_before = sum(1 for t in tracks_before if t.type == "audio")

        track_id = await client.timeline.add_track("audio", name="My Audio Track")
        assert isinstance(track_id, int)
        assert track_id > 0

        tracks_after = await client.timeline.get_tracks()
        audio_count_after = sum(1 for t in tracks_after if t.type == "audio")
        assert audio_count_after == audio_count_before + 1

    @pytest.mark.asyncio
    async def test_delete_track(self, client_with_empty_project: KdenliveClient) -> None:
        """Test deleting a track."""
        client = client_with_empty_project

        # Add a track to delete
        track_id = await client.timeline.add_track("video", name="To Delete")

        tracks_before = await client.timeline.get_tracks()
        count_before = len(tracks_before)

        result = await client.timeline.delete_track(track_id)
        assert result is True

        tracks_after = await client.timeline.get_tracks()
        assert len(tracks_after) == count_before - 1

    @pytest.mark.asyncio
    async def test_set_track_property_locked(
        self, client_with_empty_project: KdenliveClient
    ) -> None:
        """Test locking/unlocking a track."""
        client = client_with_empty_project

        track_id = await client.timeline.add_track("video", name="Lock Test")

        # Lock the track
        result = await client.timeline.set_track_property(track_id, "locked", True)
        assert result is True

        # Verify it's locked
        tracks = await client.timeline.get_tracks()
        track = next(t for t in tracks if t.id == track_id)
        assert track.locked is True

        # Unlock
        await client.timeline.set_track_property(track_id, "locked", False)
        tracks = await client.timeline.get_tracks()
        track = next(t for t in tracks if t.id == track_id)
        assert track.locked is False

    @pytest.mark.asyncio
    async def test_set_track_property_muted(
        self, client_with_empty_project: KdenliveClient
    ) -> None:
        """Test muting/unmuting a track."""
        client = client_with_empty_project

        track_id = await client.timeline.add_track("audio", name="Mute Test")

        # Mute the track
        result = await client.timeline.set_track_property(track_id, "muted", True)
        assert result is True

        tracks = await client.timeline.get_tracks()
        track = next(t for t in tracks if t.id == track_id)
        assert track.muted is True


@pytest.mark.integration
class TestClipOperations:
    """Test clip operations on timeline."""

    @pytest.mark.asyncio
    async def test_get_clips_empty_timeline(
        self, client_with_empty_project: KdenliveClient
    ) -> None:
        """Test getting clips from empty timeline."""
        clips = await client_with_empty_project.timeline.get_clips()
        assert isinstance(clips, list)
        # Empty project should have no clips
        assert len(clips) == 0

    @pytest.mark.asyncio
    async def test_insert_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test inserting a clip into the timeline."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Import clip to bin first
        clip_id = await client.bin.import_clip(str(sample_video_path))

        # Get a video track
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")

        # Insert clip
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )
        assert isinstance(timeline_clip_id, int)
        assert timeline_clip_id > 0

        # Verify clip is on timeline
        clips = await client.timeline.get_clips()
        assert len(clips) >= 1
        assert any(c.id == timeline_clip_id for c in clips)

    @pytest.mark.asyncio
    async def test_get_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test getting a single clip by ID."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Import and insert clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Get the clip
        clip = await client.timeline.get_clip(timeline_clip_id)

        assert isinstance(clip, TimelineClip)
        assert clip.id == timeline_clip_id
        assert clip.track_id == video_track.id
        assert clip.position == 0

    @pytest.mark.asyncio
    async def test_move_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test moving a clip to a new position."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Insert clip at position 0
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Move to new position
        new_position = 100
        result = await client.timeline.move_clip(
            timeline_clip_id,
            track_id=video_track.id,
            position=new_position,
        )
        assert result is True

        # Verify new position
        clip = await client.timeline.get_clip(timeline_clip_id)
        assert clip.position == new_position

    @pytest.mark.asyncio
    async def test_delete_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test deleting a clip from timeline."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Insert clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Delete it
        result = await client.timeline.delete_clip(timeline_clip_id)
        assert result is True

        # Verify it's gone
        clips = await client.timeline.get_clips()
        assert not any(c.id == timeline_clip_id for c in clips)

    @pytest.mark.asyncio
    async def test_delete_multiple_clips(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test deleting multiple clips at once."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Insert multiple clips
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")

        clip_info = await client.bin.get_clip_info(clip_id)
        duration = clip_info.duration

        clip_ids = []
        for i in range(3):
            tid = await client.timeline.insert_clip(
                bin_clip_id=clip_id,
                track_id=video_track.id,
                position=i * duration,
            )
            clip_ids.append(tid)

        # Delete all at once
        count = await client.timeline.delete_clips(clip_ids)
        assert count == 3

        # Verify all gone
        clips = await client.timeline.get_clips()
        assert not any(c.id in clip_ids for c in clips)

    @pytest.mark.asyncio
    async def test_split_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test splitting a clip."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Insert clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Get clip info for split point
        clip = await client.timeline.get_clip(timeline_clip_id)
        split_position = clip.position + clip.duration // 2

        # Split the clip
        parts = await client.timeline.split_clip(timeline_clip_id, position=split_position)

        assert len(parts) == 2
        # Original clip should now be two clips
        clips = await client.timeline.get_clips()
        assert len(clips) >= 2

    @pytest.mark.asyncio
    async def test_resize_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test resizing a clip (changing in/out points)."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Insert clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Get original clip info
        clip = await client.timeline.get_clip(timeline_clip_id)
        original_duration = clip.duration

        # Trim the clip (set new in/out points)
        new_in = 10
        new_out = original_duration - 10
        result = await client.timeline.resize_clip(
            timeline_clip_id,
            in_point=new_in,
            out_point=new_out,
        )
        assert result is True

        # Verify new duration
        clip = await client.timeline.get_clip(timeline_clip_id)
        assert clip.duration == new_out - new_in


@pytest.mark.integration
class TestTimelineNavigation:
    """Test timeline navigation operations."""

    @pytest.mark.asyncio
    async def test_seek_to_position(self, client_with_empty_project: KdenliveClient) -> None:
        """Test seeking to a specific position."""
        client = client_with_empty_project

        target_position = 100
        result = await client.timeline.seek(target_position)

        assert result == target_position

        # Verify position
        position = await client.timeline.get_position()
        assert position == target_position

    @pytest.mark.asyncio
    async def test_seek_to_start(self, client_with_empty_project: KdenliveClient) -> None:
        """Test seeking to the start."""
        client = client_with_empty_project

        # First seek somewhere
        await client.timeline.seek(500)

        # Seek back to start
        result = await client.timeline.seek(0)
        assert result == 0

    @pytest.mark.asyncio
    async def test_get_position(self, client_with_empty_project: KdenliveClient) -> None:
        """Test getting current playhead position."""
        position = await client_with_empty_project.timeline.get_position()
        assert isinstance(position, int)
        assert position >= 0


@pytest.mark.integration
class TestTimelineSelection:
    """Test timeline selection operations."""

    @pytest.mark.asyncio
    async def test_get_selection_empty(self, client_with_empty_project: KdenliveClient) -> None:
        """Test getting selection when nothing selected."""
        selection = await client_with_empty_project.timeline.get_selection()
        assert isinstance(selection, list)
        assert len(selection) == 0

    @pytest.mark.asyncio
    async def test_set_selection(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test setting clip selection."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Insert clips
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")

        clip_info = await client.bin.get_clip_info(clip_id)
        duration = clip_info.duration

        clip1_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )
        clip2_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=duration,
        )

        # Select both clips
        result = await client.timeline.set_selection([clip1_id, clip2_id])
        assert result is True

        # Verify selection
        selection = await client.timeline.get_selection()
        assert set(selection) == {clip1_id, clip2_id}

    @pytest.mark.asyncio
    async def test_clear_selection(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test clearing selection."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Insert and select a clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )
        await client.timeline.set_selection([timeline_clip_id])

        # Clear selection
        result = await client.timeline.set_selection([])
        assert result is True

        selection = await client.timeline.get_selection()
        assert len(selection) == 0


@pytest.mark.integration
class TestGetClipsByTrack:
    """Test getting clips filtered by track."""

    @pytest.mark.asyncio
    async def test_get_clips_by_track(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test getting clips for a specific track."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Add two video tracks
        track1_id = await client.timeline.add_track("video", name="Track 1")
        track2_id = await client.timeline.add_track("video", name="Track 2")

        # Import clip and add to track 1 only
        clip_id = await client.bin.import_clip(str(sample_video_path))
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=track1_id,
            position=0,
        )

        # Get clips for track 1 - should have 1
        clips_track1 = await client.timeline.get_clips(track_id=track1_id)
        assert len(clips_track1) >= 1

        # Get clips for track 2 - should have 0
        clips_track2 = await client.timeline.get_clips(track_id=track2_id)
        assert len(clips_track2) == 0
