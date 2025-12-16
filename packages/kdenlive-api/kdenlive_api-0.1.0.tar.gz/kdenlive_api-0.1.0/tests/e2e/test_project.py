"""E2E tests for project operations."""

from __future__ import annotations

from pathlib import Path

import pytest
from kdenlive_api import KdenliveClient
from kdenlive_api.types import ProjectInfo


@pytest.mark.integration
class TestProjectInfo:
    """Test project info operations."""

    @pytest.mark.asyncio
    async def test_get_info_no_project(self, client: KdenliveClient) -> None:
        """Test getting info when no project is open."""
        # Ensure no project is open
        await client.project.close(save_changes=False)

        info = await client.project.get_info()

        # Should return empty/default info
        assert isinstance(info, ProjectInfo)

    @pytest.mark.asyncio
    async def test_get_info_with_project(self, client_with_empty_project: KdenliveClient) -> None:
        """Test getting project info."""
        info = await client_with_empty_project.project.get_info()

        assert isinstance(info, ProjectInfo)
        assert info.fps > 0
        assert info.width > 0
        assert info.height > 0
        assert info.duration >= 0


@pytest.mark.integration
class TestProjectNew:
    """Test creating new projects."""

    @pytest.mark.asyncio
    async def test_new_project_default_profile(self, client: KdenliveClient) -> None:
        """Test creating new project with default profile."""
        result = await client.project.new()
        assert result is True

        info = await client.project.get_info()
        assert info.width > 0
        assert info.height > 0

        await client.project.close(save_changes=False)

    @pytest.mark.asyncio
    async def test_new_project_hd_profile(self, client: KdenliveClient) -> None:
        """Test creating new project with HD profile."""
        result = await client.project.new(profile="atsc_1080p_25")
        assert result is True

        info = await client.project.get_info()
        assert info.width == 1920
        assert info.height == 1080
        assert info.fps == 25.0

        await client.project.close(save_changes=False)

    @pytest.mark.asyncio
    async def test_new_project_4k_profile(self, client: KdenliveClient) -> None:
        """Test creating new project with 4K profile."""
        result = await client.project.new(profile="uhd2160p25")
        assert result is True

        info = await client.project.get_info()
        assert info.width == 3840
        assert info.height == 2160

        await client.project.close(save_changes=False)


@pytest.mark.integration
class TestProjectSaveOpen:
    """Test project save and open operations."""

    @pytest.mark.asyncio
    async def test_save_new_project(
        self,
        client: KdenliveClient,
        test_project_path: Path,
    ) -> None:
        """Test saving a new project."""
        await client.project.new()

        result = await client.project.save(str(test_project_path))
        assert result is True
        assert test_project_path.exists()

        await client.project.close(save_changes=False)

    @pytest.mark.asyncio
    async def test_open_project(
        self,
        client: KdenliveClient,
        test_project_path: Path,
    ) -> None:
        """Test opening an existing project."""
        # First create and save a project
        await client.project.new(profile="atsc_1080p_25")
        await client.project.save(str(test_project_path))
        await client.project.close(save_changes=False)

        # Now open it
        result = await client.project.open(str(test_project_path))
        assert result is True

        info = await client.project.get_info()
        assert info.path == str(test_project_path)

        await client.project.close(save_changes=False)

    @pytest.mark.asyncio
    async def test_save_modified_project(
        self,
        client: KdenliveClient,
        test_project_path: Path,
    ) -> None:
        """Test saving after modifications."""
        await client.project.new()
        await client.project.save(str(test_project_path))

        # Get initial modification time
        mtime1 = test_project_path.stat().st_mtime

        # Make a change (add a track)
        await client.timeline.add_track("video", name="Test Track")

        # Save again
        result = await client.project.save()
        assert result is True

        # File should be updated
        mtime2 = test_project_path.stat().st_mtime
        assert mtime2 >= mtime1

        await client.project.close(save_changes=False)

    @pytest.mark.asyncio
    async def test_save_as(
        self,
        client: KdenliveClient,
        temp_dir: Path,
    ) -> None:
        """Test Save As functionality."""
        original_path = temp_dir / "original.kdenlive"
        copy_path = temp_dir / "copy.kdenlive"

        await client.project.new()
        await client.project.save(str(original_path))

        # Save As to new location
        result = await client.project.save(str(copy_path))
        assert result is True
        assert copy_path.exists()

        # Project path should now be the new path
        info = await client.project.get_info()
        assert info.path == str(copy_path)

        await client.project.close(save_changes=False)


@pytest.mark.integration
class TestProjectClose:
    """Test project close operations."""

    @pytest.mark.asyncio
    async def test_close_without_save(self, client: KdenliveClient) -> None:
        """Test closing without saving changes."""
        await client.project.new()

        result = await client.project.close(save_changes=False)
        assert result is True

    @pytest.mark.asyncio
    async def test_close_with_save(
        self,
        client: KdenliveClient,
        test_project_path: Path,
    ) -> None:
        """Test closing with save."""
        await client.project.new()
        await client.project.save(str(test_project_path))

        # Make a modification
        await client.timeline.add_track("video")

        result = await client.project.close(save_changes=True)
        assert result is True

        # Changes should be saved
        assert test_project_path.exists()


@pytest.mark.integration
class TestProjectUndoRedo:
    """Test undo/redo operations."""

    @pytest.mark.asyncio
    async def test_undo_single_action(self, client_with_empty_project: KdenliveClient) -> None:
        """Test undoing a single action."""
        client = client_with_empty_project

        # Get initial track count
        tracks_before = await client.timeline.get_tracks()
        count_before = len(tracks_before)

        # Add a track
        await client.timeline.add_track("video", name="Undo Test")
        tracks_after_add = await client.timeline.get_tracks()
        assert len(tracks_after_add) == count_before + 1

        # Undo
        result = await client.project.undo()
        assert result is True

        # Track should be gone
        tracks_after_undo = await client.timeline.get_tracks()
        assert len(tracks_after_undo) == count_before

    @pytest.mark.asyncio
    async def test_redo_single_action(self, client_with_empty_project: KdenliveClient) -> None:
        """Test redoing a single action."""
        client = client_with_empty_project

        # Get initial track count
        tracks_before = await client.timeline.get_tracks()
        count_before = len(tracks_before)

        # Add a track then undo
        await client.timeline.add_track("video", name="Redo Test")
        await client.project.undo()

        # Redo
        result = await client.project.redo()
        assert result is True

        # Track should be back
        tracks_after_redo = await client.timeline.get_tracks()
        assert len(tracks_after_redo) == count_before + 1

    @pytest.mark.asyncio
    async def test_multiple_undo_redo(self, client_with_empty_project: KdenliveClient) -> None:
        """Test multiple undo/redo operations."""
        client = client_with_empty_project

        # Perform multiple actions
        await client.timeline.add_track("video", name="Track 1")
        await client.timeline.add_track("video", name="Track 2")
        await client.timeline.add_track("audio", name="Track 3")

        tracks = await client.timeline.get_tracks()
        initial_count = len(tracks)

        # Undo all three
        await client.project.undo()
        await client.project.undo()
        await client.project.undo()

        tracks_after_undo = await client.timeline.get_tracks()
        assert len(tracks_after_undo) == initial_count - 3

        # Redo two
        await client.project.redo()
        await client.project.redo()

        tracks_after_redo = await client.timeline.get_tracks()
        assert len(tracks_after_redo) == initial_count - 1

    @pytest.mark.asyncio
    async def test_undo_nothing_to_undo(self, client: KdenliveClient) -> None:
        """Test undo when nothing to undo."""
        await client.project.new()

        # Undo on fresh project should not fail
        result = await client.project.undo()
        # Result may be False if nothing to undo
        assert isinstance(result, bool)

        await client.project.close(save_changes=False)


@pytest.mark.integration
class TestProjectModifiedState:
    """Test project modified state tracking."""

    @pytest.mark.asyncio
    async def test_new_project_not_modified(self, client: KdenliveClient) -> None:
        """Test that new project is not marked as modified."""
        await client.project.new()

        info = await client.project.get_info()
        assert info.modified is False

        await client.project.close(save_changes=False)

    @pytest.mark.asyncio
    async def test_modified_after_change(self, client: KdenliveClient) -> None:
        """Test that project is marked modified after change."""
        await client.project.new()

        # Make a change
        await client.timeline.add_track("video")

        info = await client.project.get_info()
        assert info.modified is True

        await client.project.close(save_changes=False)

    @pytest.mark.asyncio
    async def test_not_modified_after_save(
        self,
        client: KdenliveClient,
        test_project_path: Path,
    ) -> None:
        """Test that project is not modified after save."""
        await client.project.new()
        await client.timeline.add_track("video")

        # Should be modified
        info = await client.project.get_info()
        assert info.modified is True

        # Save
        await client.project.save(str(test_project_path))

        # Should no longer be modified
        info = await client.project.get_info()
        assert info.modified is False

        await client.project.close(save_changes=False)
