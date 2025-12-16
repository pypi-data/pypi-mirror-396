"""E2E tests for complete editing workflows.

These tests verify end-to-end scenarios that combine multiple operations.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from conftest import skip_slow_tests, skip_without_sample_video
from kdenlive_api import KdenliveClient


@pytest.mark.integration
class TestBasicEditingWorkflow:
    """Test basic video editing workflow."""

    @pytest.mark.asyncio
    async def test_import_arrange_workflow(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test importing clips and arranging on timeline."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Step 1: Import clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        assert clip_id

        # Step 2: Get clip info
        clip_info = await client.bin.get_clip_info(clip_id)
        assert clip_info.duration > 0

        # Step 3: Add to timeline
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")

        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )
        assert timeline_clip_id > 0

        # Step 4: Verify timeline has content
        timeline_info = await client.timeline.get_info()
        assert timeline_info.duration > 0

        clips = await client.timeline.get_clips()
        assert len(clips) == 1

    @pytest.mark.asyncio
    async def test_multi_clip_arrangement(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test arranging multiple clips on timeline."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Import same clip multiple times (simulating different clips)
        clip_id = await client.bin.import_clip(str(sample_video_path))
        clip_info = await client.bin.get_clip_info(clip_id)
        duration = clip_info.duration

        # Get video track
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")

        # Add three clips in sequence
        positions = [0, duration, duration * 2]
        clip_ids = []
        for pos in positions:
            tid = await client.timeline.insert_clip(
                bin_clip_id=clip_id,
                track_id=video_track.id,
                position=pos,
            )
            clip_ids.append(tid)

        # Verify all clips on timeline
        clips = await client.timeline.get_clips()
        assert len(clips) == 3

        # Verify positions
        for i, clip in enumerate(sorted(clips, key=lambda c: c.position)):
            assert clip.position == positions[i]


@pytest.mark.integration
class TestEffectsWorkflow:
    """Test effects editing workflow."""

    @pytest.mark.asyncio
    async def test_apply_effect_workflow(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test applying and configuring an effect."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup: import and add clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Step 1: Find an effect
        effects = await client.effects.list_available()
        video_effects = [e for e in effects if e.category == "video"]
        assert len(video_effects) > 0

        effect = video_effects[0]

        # Step 2: Add effect to clip
        effect_instance = await client.effects.add(effect.id, timeline_clip_id)
        assert effect_instance

        # Step 3: Get effect parameters
        info = await client.effects.get_info(effect.id)

        # Step 4: Modify a parameter if available
        if info.parameters:
            param = info.parameters[0]
            await client.effects.set_property(
                timeline_clip_id,
                effect.id,
                param.name,
                param.default if param.default else 0.5,
            )

        # Step 5: Verify effect is applied
        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)
        assert any(e.id == effect.id for e in clip_effects)

    @pytest.mark.asyncio
    async def test_effect_animation_workflow(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test animating an effect with keyframes."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Get clip duration
        clip = await client.timeline.get_clip(timeline_clip_id)

        # Add effect
        effects = await client.effects.list_available()
        effect = next((e for e in effects if e.category == "video"), effects[0])
        await client.effects.add(effect.id, timeline_clip_id)

        # Get parameter to animate
        info = await client.effects.get_info(effect.id)
        if not info.parameters:
            pytest.skip("Effect has no parameters to animate")

        param = info.parameters[0]

        # Create fade-in animation with keyframes
        # Start value at beginning
        await client.effects.set_keyframe(
            timeline_clip_id,
            effect.id,
            param.name,
            position=0,
            value=0.0,
        )

        # End value at midpoint
        await client.effects.set_keyframe(
            timeline_clip_id,
            effect.id,
            param.name,
            position=clip.duration // 2,
            value=1.0,
        )

        # Verify keyframes
        keyframes = await client.effects.get_keyframes(
            timeline_clip_id,
            effect.id,
            param.name,
        )
        assert len(keyframes) >= 2


@pytest.mark.integration
class TestProjectWorkflow:
    """Test project management workflow."""

    @pytest.mark.asyncio
    async def test_create_edit_save_workflow(
        self,
        client: KdenliveClient,
        sample_video_path: Path | None,
        test_project_path: Path,
    ) -> None:
        """Test full project create/edit/save workflow."""
        skip_without_sample_video(sample_video_path)

        # Step 1: Create new project
        await client.project.new(profile="atsc_1080p_25")

        # Step 2: Organize bin with folders
        folder_id = await client.bin.create_folder("Raw Footage")

        # Step 3: Import media
        clip_id = await client.bin.import_clip(
            str(sample_video_path),
            folder_id=folder_id,
        )

        # Step 4: Add tracks
        await client.timeline.add_track("video", name="Main Video")
        await client.timeline.add_track("audio", name="Main Audio")

        # Step 5: Add clip to timeline
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.name == "Main Video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Step 6: Save project
        await client.project.save(str(test_project_path))

        # Verify project file exists
        assert test_project_path.exists()

        # Step 7: Close project
        await client.project.close(save_changes=False)

    @pytest.mark.asyncio
    async def test_open_modify_save_workflow(
        self,
        client: KdenliveClient,
        sample_video_path: Path | None,
        test_project_path: Path,
    ) -> None:
        """Test opening, modifying, and saving existing project."""
        skip_without_sample_video(sample_video_path)

        # First create a project
        await client.project.new()
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )
        await client.project.save(str(test_project_path))
        await client.project.close(save_changes=False)

        # Now open and modify
        await client.project.open(str(test_project_path))

        # Make modifications
        tracks = await client.timeline.get_tracks()
        initial_count = len(tracks)

        await client.timeline.add_track("video", name="New Track")

        # Verify modification
        tracks = await client.timeline.get_tracks()
        assert len(tracks) == initial_count + 1

        # Save and close
        await client.project.save()
        await client.project.close(save_changes=False)


@pytest.mark.integration
@pytest.mark.slow
class TestRenderWorkflow:
    """Test complete render workflow."""

    @pytest.mark.asyncio
    async def test_full_render_workflow(
        self,
        client: KdenliveClient,
        sample_video_path: Path | None,
        test_project_path: Path,
        test_output_path: Path,
    ) -> None:
        """Test complete workflow from import to render."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()

        # Step 1: Create project
        await client.project.new(profile="atsc_1080p_25")

        # Step 2: Import media
        clip_id = await client.bin.import_clip(str(sample_video_path))

        # Step 3: Add to timeline
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Step 4: Trim clip to short duration (1 second)
        await client.timeline.resize_clip(timeline_clip_id, in_point=0, out_point=25)

        # Step 5: Add an effect
        effects = await client.effects.list_available()
        effect = next((e for e in effects if e.category == "video"), effects[0])
        await client.effects.add(effect.id, timeline_clip_id)

        # Step 6: Save project
        await client.project.save(str(test_project_path))

        # Step 7: Start render
        presets = await client.render.get_presets()
        job = await client.render.start(presets[0].name, str(test_output_path))

        # Step 8: Wait for completion
        max_wait = 60
        elapsed = 0
        while elapsed < max_wait:
            status = await client.render.get_status(job.job_id)
            if status.status == "completed":
                break
            if status.status == "error":
                pytest.fail("Render failed")
            await asyncio.sleep(1)
            elapsed += 1

        # Step 9: Verify output
        assert test_output_path.exists()

        # Cleanup
        await client.project.close(save_changes=False)


@pytest.mark.integration
class TestUndoRedoWorkflow:
    """Test undo/redo in editing workflow."""

    @pytest.mark.asyncio
    async def test_undo_redo_edit_workflow(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test undo/redo during editing."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Import and add clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")

        # Action 1: Insert clip
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        clips = await client.timeline.get_clips()
        assert len(clips) == 1

        # Action 2: Add effect
        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, timeline_clip_id)

        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)
        assert len(clip_effects) == 1

        # Undo effect
        await client.project.undo()
        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)
        assert len(clip_effects) == 0

        # Redo effect
        await client.project.redo()
        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)
        assert len(clip_effects) == 1

        # Undo both actions
        await client.project.undo()  # Undo effect
        await client.project.undo()  # Undo clip insert

        clips = await client.timeline.get_clips()
        assert len(clips) == 0


@pytest.mark.integration
class TestOrganizationWorkflow:
    """Test media organization workflow."""

    @pytest.mark.asyncio
    async def test_bin_organization_workflow(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test organizing media in the bin."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Create folder structure
        scenes_folder = await client.bin.create_folder("Scenes")
        broll_folder = await client.bin.create_folder("B-Roll", parent_id=scenes_folder)
        _audio_folder = await client.bin.create_folder("Audio")

        # Import clips
        clip1_id = await client.bin.import_clip(str(sample_video_path))
        clip2_id = await client.bin.import_clip(str(sample_video_path))
        clip3_id = await client.bin.import_clip(str(sample_video_path))

        # Organize clips into folders
        await client.bin.move_item(clip1_id, scenes_folder)
        await client.bin.move_item(clip2_id, broll_folder)

        # Rename clips
        await client.bin.rename_item(clip1_id, "Main Scene")
        await client.bin.rename_item(clip2_id, "Cutaway 1")
        await client.bin.rename_item(clip3_id, "Unused Footage")

        # Verify organization
        scenes_clips = await client.bin.list_clips(folder_id=scenes_folder)
        broll_clips = await client.bin.list_clips(folder_id=broll_folder)

        assert any(c.id == clip1_id for c in scenes_clips)
        assert any(c.id == clip2_id for c in broll_clips)

        # Clean up unused
        await client.bin.delete_clip(clip3_id)

        all_clips = await client.bin.list_clips()
        assert not any(c.id == clip3_id for c in all_clips)


@pytest.mark.integration
class TestMultiTrackWorkflow:
    """Test multi-track editing workflow."""

    @pytest.mark.asyncio
    async def test_multi_track_edit(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test editing with multiple tracks."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Create custom track layout
        main_video_id = await client.timeline.add_track("video", name="Main Video")
        overlay_id = await client.timeline.add_track("video", name="Overlay")
        _main_audio_id = await client.timeline.add_track("audio", name="Main Audio")
        _music_id = await client.timeline.add_track("audio", name="Music")

        # Import clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        clip_info = await client.bin.get_clip_info(clip_id)
        duration = clip_info.duration

        # Add main video
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=main_video_id,
            position=0,
        )

        # Add overlay (offset)
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=overlay_id,
            position=duration // 4,
        )

        # Verify multi-track setup
        clips = await client.timeline.get_clips()
        assert len(clips) >= 2

        main_clips = await client.timeline.get_clips(track_id=main_video_id)
        overlay_clips = await client.timeline.get_clips(track_id=overlay_id)

        assert len(main_clips) >= 1
        assert len(overlay_clips) >= 1

    @pytest.mark.asyncio
    async def test_track_locking_workflow(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test track locking during editing."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup tracks with content
        track_id = await client.timeline.add_track("video", name="Locked Track")

        clip_id = await client.bin.import_clip(str(sample_video_path))
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=track_id,
            position=0,
        )

        # Lock the track
        await client.timeline.set_track_property(track_id, "locked", True)

        # Verify locked
        tracks = await client.timeline.get_tracks()
        locked_track = next(t for t in tracks if t.id == track_id)
        assert locked_track.locked is True

        # Unlock for further editing
        await client.timeline.set_track_property(track_id, "locked", False)

        tracks = await client.timeline.get_tracks()
        unlocked_track = next(t for t in tracks if t.id == track_id)
        assert unlocked_track.locked is False
