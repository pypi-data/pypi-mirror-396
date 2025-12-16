"""E2E tests for render operations."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from conftest import skip_slow_tests, skip_without_sample_video
from kdenlive_api import KdenliveClient
from kdenlive_api.types import RenderJob, RenderPreset, RenderPresetDetail, RenderStatus


@pytest.mark.integration
class TestRenderPresets:
    """Test render preset operations."""

    @pytest.mark.asyncio
    async def test_get_presets(self, client: KdenliveClient) -> None:
        """Test getting available render presets."""
        presets = await client.render.get_presets()

        assert isinstance(presets, list)
        assert len(presets) > 0
        assert all(isinstance(p, RenderPreset) for p in presets)

    @pytest.mark.asyncio
    async def test_preset_has_name_and_extension(self, client: KdenliveClient) -> None:
        """Test that presets have name and extension."""
        presets = await client.render.get_presets()

        for preset in presets:
            assert preset.name
            assert preset.extension

    @pytest.mark.asyncio
    async def test_get_preset_info(self, client: KdenliveClient) -> None:
        """Test getting detailed preset info."""
        presets = await client.render.get_presets()
        preset = presets[0]

        info = await client.render.get_preset_info(preset.name)

        assert isinstance(info, RenderPresetDetail)
        assert info.name == preset.name
        assert info.extension == preset.extension
        assert isinstance(info.params, dict)


@pytest.mark.integration
class TestRenderStart:
    """Test starting render jobs."""

    @pytest.mark.asyncio
    async def test_start_render(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        test_output_path: Path,
    ) -> None:
        """Test starting a render job."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Add content to timeline
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Get a preset
        presets = await client.render.get_presets()
        preset = presets[0]

        # Start render
        job = await client.render.start(preset.name, str(test_output_path))

        assert isinstance(job, RenderJob)
        assert job.job_id
        assert job.output_path == str(test_output_path)
        assert job.status in ("pending", "running")

        # Stop the job (don't wait for completion in test)
        await client.render.stop(job.job_id)

    @pytest.mark.asyncio
    async def test_start_render_with_custom_output_path(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        temp_dir: Path,
    ) -> None:
        """Test render with custom output path."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup timeline
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Custom path
        custom_path = temp_dir / "custom_output" / "render.mp4"
        presets = await client.render.get_presets()
        preset = presets[0]

        job = await client.render.start(preset.name, str(custom_path))

        assert job.output_path == str(custom_path)

        await client.render.stop(job.job_id)


@pytest.mark.integration
class TestRenderStop:
    """Test stopping render jobs."""

    @pytest.mark.asyncio
    async def test_stop_render(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        test_output_path: Path,
    ) -> None:
        """Test stopping a running render."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup and start render
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        presets = await client.render.get_presets()
        job = await client.render.start(presets[0].name, str(test_output_path))

        # Stop it
        result = await client.render.stop(job.job_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_stop_all_renders(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        temp_dir: Path,
    ) -> None:
        """Test stopping all render jobs."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup timeline
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        presets = await client.render.get_presets()

        # Start multiple renders
        _job1 = await client.render.start(presets[0].name, str(temp_dir / "output1.mp4"))
        _job2 = await client.render.start(presets[0].name, str(temp_dir / "output2.mp4"))

        # Stop all
        count = await client.render.stop_all()
        assert count >= 2


@pytest.mark.integration
class TestRenderStatus:
    """Test render status operations."""

    @pytest.mark.asyncio
    async def test_get_status(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        test_output_path: Path,
    ) -> None:
        """Test getting render job status."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup and start render
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        presets = await client.render.get_presets()
        job = await client.render.start(presets[0].name, str(test_output_path))

        # Get status
        status = await client.render.get_status(job.job_id)

        assert isinstance(status, RenderStatus)
        assert status.job_id == job.job_id
        assert status.status in ("pending", "running", "completed", "error")
        assert 0 <= status.progress <= 100

        await client.render.stop(job.job_id)

    @pytest.mark.asyncio
    async def test_status_progress_updates(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        test_output_path: Path,
    ) -> None:
        """Test that progress updates during render."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup a longer clip for visible progress
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        presets = await client.render.get_presets()
        job = await client.render.start(presets[0].name, str(test_output_path))

        # Check status a few times
        progress_values = []
        for _ in range(5):
            status = await client.render.get_status(job.job_id)
            progress_values.append(status.progress)
            if status.status in ("completed", "error"):
                break
            await asyncio.sleep(0.5)

        await client.render.stop(job.job_id)

        # Progress should be >= 0 and <= 100
        assert all(0 <= p <= 100 for p in progress_values)


@pytest.mark.integration
class TestRenderJobs:
    """Test render job listing."""

    @pytest.mark.asyncio
    async def test_get_jobs_empty(self, client_with_empty_project: KdenliveClient) -> None:
        """Test getting jobs when none are running."""
        jobs = await client_with_empty_project.render.get_jobs()
        assert isinstance(jobs, list)

    @pytest.mark.asyncio
    async def test_get_jobs_with_active(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        test_output_path: Path,
    ) -> None:
        """Test getting jobs when render is active."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup and start render
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        presets = await client.render.get_presets()
        job = await client.render.start(presets[0].name, str(test_output_path))

        # Get jobs
        jobs = await client.render.get_jobs()

        assert len(jobs) >= 1
        assert any(j.job_id == job.job_id for j in jobs)

        await client.render.stop(job.job_id)


@pytest.mark.integration
class TestRenderActiveJob:
    """Test getting active render job."""

    @pytest.mark.asyncio
    async def test_get_active_job_none(self, client_with_empty_project: KdenliveClient) -> None:
        """Test getting active job when none running."""
        active = await client_with_empty_project.render.get_active_job()
        assert active is None

    @pytest.mark.asyncio
    async def test_get_active_job(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        test_output_path: Path,
    ) -> None:
        """Test getting active job during render."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup and start render
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        presets = await client.render.get_presets()
        job = await client.render.start(presets[0].name, str(test_output_path))

        # Get active job
        active = await client.render.get_active_job()

        assert active is not None
        assert isinstance(active, RenderStatus)
        assert active.job_id == job.job_id

        await client.render.stop(job.job_id)


@pytest.mark.integration
class TestRenderSetOutput:
    """Test setting default output path."""

    @pytest.mark.asyncio
    async def test_set_output_path(
        self,
        client_with_empty_project: KdenliveClient,
        temp_dir: Path,
    ) -> None:
        """Test setting default output path."""
        client = client_with_empty_project

        output_dir = temp_dir / "default_output"
        result = await client.render.set_output(str(output_dir))

        assert result is True


@pytest.mark.integration
@pytest.mark.slow
class TestRenderComplete:
    """Test complete render operations (slow tests)."""

    @pytest.mark.asyncio
    async def test_render_to_completion(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        test_output_path: Path,
    ) -> None:
        """Test rendering a project to completion."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup a short clip
        clip_id = await client.bin.import_clip(str(sample_video_path))

        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")

        # Insert just 1 second of video
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )
        # Trim to 1 second (25 frames at 25fps)
        clips = await client.timeline.get_clips()
        if clips:
            await client.timeline.resize_clip(clips[0].id, in_point=0, out_point=25)

        presets = await client.render.get_presets()
        job = await client.render.start(presets[0].name, str(test_output_path))

        # Wait for completion (with timeout)
        max_wait = 60  # seconds
        elapsed = 0
        while elapsed < max_wait:
            status = await client.render.get_status(job.job_id)
            if status.status == "completed":
                break
            if status.status == "error":
                pytest.fail(f"Render failed: {status}")
            await asyncio.sleep(1)
            elapsed += 1

        assert status.status == "completed"
        assert test_output_path.exists()

    @pytest.mark.asyncio
    async def test_render_watch_progress(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        test_output_path: Path,
    ) -> None:
        """Test watching render progress with async iterator."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup short clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        clips = await client.timeline.get_clips()
        if clips:
            await client.timeline.resize_clip(clips[0].id, in_point=0, out_point=25)

        presets = await client.render.get_presets()
        job = await client.render.start(presets[0].name, str(test_output_path))

        # Watch progress
        progress_updates = []
        async for progress in client.render.watch(job.job_id):
            progress_updates.append(progress)
            if progress.progress >= 100:
                break

        assert len(progress_updates) > 0
        # Final progress should be 100
        assert progress_updates[-1].progress == 100


@pytest.mark.integration
class TestRenderWithGuides:
    """Test rendering with guide markers."""

    @pytest.mark.asyncio
    async def test_start_with_guides(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
        temp_dir: Path,
    ) -> None:
        """Test rendering using guide markers for chapters."""
        skip_without_sample_video(sample_video_path)
        skip_slow_tests()
        client = client_with_empty_project

        # Setup timeline with clip
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Note: This test assumes guides are already set in the project
        # or there's a method to add timeline guides (not clip markers)

        presets = await client.render.get_presets()
        output_dir = temp_dir / "guide_output"
        output_dir.mkdir(exist_ok=True)

        jobs = await client.render.start_with_guides(presets[0].name, str(output_dir))

        assert isinstance(jobs, list)

        # Clean up
        for job in jobs:
            await client.render.stop(job.job_id)
