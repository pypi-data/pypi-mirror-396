"""E2E tests for bin (project bin/media library) operations."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import (
    skip_without_sample_audio,
    skip_without_sample_video,
)
from kdenlive_api import KdenliveClient
from kdenlive_api.types import ClipInfo


@pytest.mark.integration
class TestBinListClips:
    """Test listing clips in the bin."""

    @pytest.mark.asyncio
    async def test_list_clips_empty(self, client_with_empty_project: KdenliveClient) -> None:
        """Test listing clips in empty project."""
        clips = await client_with_empty_project.bin.list_clips()

        assert isinstance(clips, list)
        assert len(clips) == 0

    @pytest.mark.asyncio
    async def test_list_clips_with_content(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test listing clips after import."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Import a clip
        await client.bin.import_clip(str(sample_video_path))

        clips = await client.bin.list_clips()

        assert len(clips) >= 1
        assert isinstance(clips[0], ClipInfo)


@pytest.mark.integration
class TestBinImport:
    """Test importing media into the bin."""

    @pytest.mark.asyncio
    async def test_import_video_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test importing a video file."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))

        assert isinstance(clip_id, str)
        assert len(clip_id) > 0

        # Verify the clip exists
        clips = await client.bin.list_clips()
        assert any(c.id == clip_id for c in clips)

    @pytest.mark.asyncio
    async def test_import_audio_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_audio_path: Path | None,
    ) -> None:
        """Test importing an audio file."""
        skip_without_sample_audio(sample_audio_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_audio_path))

        assert isinstance(clip_id, str)

        # Verify it's an audio clip
        info = await client.bin.get_clip_info(clip_id)
        assert info.type == "audio" or info.has_audio is True

    @pytest.mark.asyncio
    async def test_import_multiple_clips(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        sample_audio_path: Path | None,
    ) -> None:
        """Test importing multiple files at once."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        paths = [str(sample_video_path)]
        if sample_audio_path:
            paths.append(str(sample_audio_path))

        clip_ids = await client.bin.import_clips(paths)

        assert isinstance(clip_ids, list)
        assert len(clip_ids) == len(paths)

    @pytest.mark.asyncio
    async def test_import_to_folder(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test importing a clip to a specific folder."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Create a folder first
        folder_id = await client.bin.create_folder("Test Folder")

        # Import to that folder
        clip_id = await client.bin.import_clip(
            str(sample_video_path),
            folder_id=folder_id,
        )

        # List clips in folder
        clips = await client.bin.list_clips(folder_id=folder_id)
        assert any(c.id == clip_id for c in clips)


@pytest.mark.integration
class TestBinClipInfo:
    """Test getting clip information."""

    @pytest.mark.asyncio
    async def test_get_clip_info(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test getting detailed clip info."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))
        info = await client.bin.get_clip_info(clip_id)

        assert isinstance(info, ClipInfo)
        assert info.id == clip_id
        assert info.duration > 0
        assert info.url == str(sample_video_path)

    @pytest.mark.asyncio
    async def test_clip_info_video_properties(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test video clip has correct properties."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))
        info = await client.bin.get_clip_info(clip_id)

        assert info.has_video is True
        assert info.width > 0
        assert info.height > 0


@pytest.mark.integration
class TestBinDelete:
    """Test deleting clips from the bin."""

    @pytest.mark.asyncio
    async def test_delete_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test deleting a single clip."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))

        result = await client.bin.delete_clip(clip_id)
        assert result is True

        # Verify it's gone
        clips = await client.bin.list_clips()
        assert not any(c.id == clip_id for c in clips)

    @pytest.mark.asyncio
    async def test_delete_multiple_clips(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test deleting multiple clips at once."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Import multiple copies
        clip_ids = await client.bin.import_clips(
            [
                str(sample_video_path),
                str(sample_video_path),
                str(sample_video_path),
            ]
        )

        count = await client.bin.delete_clips(clip_ids)
        assert count == 3

        # Verify all gone
        clips = await client.bin.list_clips()
        assert not any(c.id in clip_ids for c in clips)


@pytest.mark.integration
class TestBinFolders:
    """Test folder management in the bin."""

    @pytest.mark.asyncio
    async def test_list_folders_empty(self, client_with_empty_project: KdenliveClient) -> None:
        """Test listing folders in empty project."""
        folders = await client_with_empty_project.bin.list_folders()
        assert isinstance(folders, list)

    @pytest.mark.asyncio
    async def test_create_folder(self, client_with_empty_project: KdenliveClient) -> None:
        """Test creating a folder."""
        client = client_with_empty_project

        folder_id = await client.bin.create_folder("My Folder")

        assert isinstance(folder_id, str)
        assert len(folder_id) > 0

        # Verify folder exists
        folders = await client.bin.list_folders()
        assert any(f.id == folder_id for f in folders)

    @pytest.mark.asyncio
    async def test_create_nested_folder(self, client_with_empty_project: KdenliveClient) -> None:
        """Test creating a nested folder."""
        client = client_with_empty_project

        parent_id = await client.bin.create_folder("Parent")
        child_id = await client.bin.create_folder("Child", parent_id=parent_id)

        # Verify parent-child relationship
        folders = await client.bin.list_folders()
        child_folder = next(f for f in folders if f.id == child_id)
        assert child_folder.parent_id == parent_id

    @pytest.mark.asyncio
    async def test_delete_folder(self, client_with_empty_project: KdenliveClient) -> None:
        """Test deleting a folder."""
        client = client_with_empty_project

        folder_id = await client.bin.create_folder("To Delete")

        result = await client.bin.delete_folder(folder_id)
        assert result is True

        # Verify it's gone
        folders = await client.bin.list_folders()
        assert not any(f.id == folder_id for f in folders)

    @pytest.mark.asyncio
    async def test_list_clips_in_folder(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test listing clips filtered by folder."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Create folders
        folder1_id = await client.bin.create_folder("Folder 1")
        folder2_id = await client.bin.create_folder("Folder 2")

        # Import to folder 1
        clip_id = await client.bin.import_clip(
            str(sample_video_path),
            folder_id=folder1_id,
        )

        # List folder 1 - should have the clip
        clips_folder1 = await client.bin.list_clips(folder_id=folder1_id)
        assert any(c.id == clip_id for c in clips_folder1)

        # List folder 2 - should be empty
        clips_folder2 = await client.bin.list_clips(folder_id=folder2_id)
        assert len(clips_folder2) == 0


@pytest.mark.integration
class TestBinRename:
    """Test renaming items in the bin."""

    @pytest.mark.asyncio
    async def test_rename_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test renaming a clip."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))

        new_name = "Renamed Clip"
        result = await client.bin.rename_item(clip_id, new_name)
        assert result is True

        # Verify the name changed
        info = await client.bin.get_clip_info(clip_id)
        assert info.name == new_name

    @pytest.mark.asyncio
    async def test_rename_folder(self, client_with_empty_project: KdenliveClient) -> None:
        """Test renaming a folder."""
        client = client_with_empty_project

        folder_id = await client.bin.create_folder("Original Name")

        new_name = "New Folder Name"
        result = await client.bin.rename_item(folder_id, new_name)
        assert result is True

        # Verify the name changed
        folders = await client.bin.list_folders()
        folder = next(f for f in folders if f.id == folder_id)
        assert folder.name == new_name


@pytest.mark.integration
class TestBinMoveItems:
    """Test moving items between folders."""

    @pytest.mark.asyncio
    async def test_move_clip_to_folder(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test moving a clip to a folder."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Import clip to root
        clip_id = await client.bin.import_clip(str(sample_video_path))

        # Create folder
        folder_id = await client.bin.create_folder("Target Folder")

        # Move clip
        result = await client.bin.move_item(clip_id, folder_id)
        assert result is True

        # Verify clip is in folder
        clips = await client.bin.list_clips(folder_id=folder_id)
        assert any(c.id == clip_id for c in clips)


@pytest.mark.integration
class TestBinMarkers:
    """Test clip marker operations."""

    @pytest.mark.asyncio
    async def test_get_markers_empty(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test getting markers from clip with no markers."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))
        markers = await client.bin.get_clip_markers(clip_id)

        assert isinstance(markers, list)
        assert len(markers) == 0

    @pytest.mark.asyncio
    async def test_add_marker(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test adding a marker to a clip."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))

        marker_id = await client.bin.add_clip_marker(
            clip_id,
            position=100,
            comment="Test marker",
        )
        assert isinstance(marker_id, int)

        # Verify marker exists
        markers = await client.bin.get_clip_markers(clip_id)
        assert len(markers) >= 1
        marker = next(m for m in markers if m.id == marker_id)
        assert marker.position == 100
        assert marker.comment == "Test marker"

    @pytest.mark.asyncio
    async def test_add_multiple_markers(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test adding multiple markers to a clip."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))

        await client.bin.add_clip_marker(clip_id, position=100, comment="Marker 1")
        await client.bin.add_clip_marker(clip_id, position=200, comment="Marker 2")
        await client.bin.add_clip_marker(clip_id, position=300, comment="Marker 3")

        markers = await client.bin.get_clip_markers(clip_id)
        assert len(markers) >= 3

    @pytest.mark.asyncio
    async def test_delete_marker(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test deleting a marker."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))
        marker_id = await client.bin.add_clip_marker(
            clip_id,
            position=100,
            comment="To delete",
        )

        result = await client.bin.delete_clip_marker(clip_id, marker_id)
        assert result is True

        # Verify it's gone
        markers = await client.bin.get_clip_markers(clip_id)
        assert not any(m.id == marker_id for m in markers)
