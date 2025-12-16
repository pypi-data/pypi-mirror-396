"""Tests for RenderAPI."""

from __future__ import annotations

import pytest
from conftest import MockWebSocketServer
from kdenlive_api import KdenliveClient
from kdenlive_api.types import RenderJob, RenderPreset, RenderPresetDetail, RenderStatus


class TestRenderGetPresets:
    """Test render.get_presets method."""

    @pytest.mark.asyncio
    async def test_get_presets(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting render presets."""
        client, server = client_with_server

        server.register_handler(
            "render.getPresets",
            {
                "presets": [
                    {"name": "YouTube 1080p", "extension": "mp4"},
                    {"name": "ProRes 422", "extension": "mov"},
                ]
            },
        )

        presets = await client.render.get_presets()

        assert len(presets) == 2
        assert isinstance(presets[0], RenderPreset)
        assert presets[0].name == "YouTube 1080p"


class TestRenderGetPresetInfo:
    """Test render.get_preset_info method."""

    @pytest.mark.asyncio
    async def test_get_preset_info(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting preset details."""
        client, server = client_with_server

        server.register_handler(
            "render.getPresetInfo",
            {
                "name": "YouTube 1080p",
                "extension": "mp4",
                "params": {"crf": "18", "preset": "medium"},
            },
        )

        info = await client.render.get_preset_info("YouTube 1080p")

        assert isinstance(info, RenderPresetDetail)
        assert info.params["crf"] == "18"


class TestRenderStart:
    """Test render.start method."""

    @pytest.mark.asyncio
    async def test_start_render(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test starting render job."""
        client, server = client_with_server

        server.register_handler(
            "render.start",
            {
                "jobId": "job_123",
                "outputPath": "/output/video.mp4",
                "status": "pending",
                "progress": 0,
            },
        )

        job = await client.render.start("YouTube 1080p", "/output/video.mp4")

        assert isinstance(job, RenderJob)
        assert job.job_id == "job_123"
        assert server.requests[0]["params"]["presetName"] == "YouTube 1080p"
        assert server.requests[0]["params"]["outputPath"] == "/output/video.mp4"


class TestRenderStartWithGuides:
    """Test render.start_with_guides method."""

    @pytest.mark.asyncio
    async def test_start_with_guides(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test starting render with guide markers."""
        client, server = client_with_server

        server.register_handler(
            "render.startWithGuides",
            {
                "jobs": [
                    {"jobId": "job_124", "outputPath": "/output/Scene 1.mp4"},
                    {"jobId": "job_125", "outputPath": "/output/Scene 2.mp4"},
                ]
            },
        )

        jobs = await client.render.start_with_guides("YouTube 1080p", "/output/")

        assert len(jobs) == 2
        assert jobs[0].output_path == "/output/Scene 1.mp4"


class TestRenderStop:
    """Test render.stop method."""

    @pytest.mark.asyncio
    async def test_stop_render(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test stopping render job."""
        client, server = client_with_server

        server.register_handler("render.stop", {"stopped": True})

        result = await client.render.stop("job_123")

        assert result is True
        assert server.requests[0]["params"]["jobId"] == "job_123"

    @pytest.mark.asyncio
    async def test_stop_all(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test stopping all render jobs."""
        client, server = client_with_server

        server.register_handler("render.stopAll", {"count": 2})

        result = await client.render.stop_all()

        assert result == 2


class TestRenderGetStatus:
    """Test render.get_status method."""

    @pytest.mark.asyncio
    async def test_get_status(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting render status."""
        client, server = client_with_server

        server.register_handler(
            "render.getStatus",
            {
                "jobId": "job_123",
                "status": "running",
                "progress": 45,
                "frame": 3375,
                "totalFrames": 7500,
                "eta": 120,
            },
        )

        status = await client.render.get_status("job_123")

        assert isinstance(status, RenderStatus)
        assert status.progress == 45
        assert status.frame == 3375


class TestRenderGetJobs:
    """Test render.get_jobs method."""

    @pytest.mark.asyncio
    async def test_get_jobs(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting all render jobs."""
        client, server = client_with_server

        server.register_handler(
            "render.getJobs",
            {
                "jobs": [
                    {
                        "jobId": "job_123",
                        "outputPath": "/out/1.mp4",
                        "status": "running",
                        "progress": 45,
                    },
                    {
                        "jobId": "job_124",
                        "outputPath": "/out/2.mp4",
                        "status": "pending",
                        "progress": 0,
                    },
                ]
            },
        )

        jobs = await client.render.get_jobs()

        assert len(jobs) == 2
        assert isinstance(jobs[0], RenderJob)


class TestRenderGetActiveJob:
    """Test render.get_active_job method."""

    @pytest.mark.asyncio
    async def test_get_active_job(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting active render job."""
        client, server = client_with_server

        server.register_handler(
            "render.getActiveJob",
            {
                "jobId": "job_123",
                "status": "running",
                "progress": 45,
                "frame": 3375,
                "totalFrames": 7500,
                "eta": 120,
            },
        )

        active = await client.render.get_active_job()

        assert active is not None
        assert isinstance(active, RenderStatus)
        assert active.progress == 45

    @pytest.mark.asyncio
    async def test_get_active_job_none(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting active job when none running."""
        client, server = client_with_server

        server.register_handler("render.getActiveJob", {})

        active = await client.render.get_active_job()

        assert active is None


class TestRenderSetOutput:
    """Test render.set_output method."""

    @pytest.mark.asyncio
    async def test_set_output(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test setting default output path."""
        client, server = client_with_server

        server.register_handler("render.setOutput", {"set": True})

        result = await client.render.set_output("/default/output/")

        assert result is True
        assert server.requests[0]["params"]["defaultPath"] == "/default/output/"
