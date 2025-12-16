"""Render API."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from kdenlive_api.types import (
    GuideRenderJob,
    RenderJob,
    RenderPreset,
    RenderPresetDetail,
    RenderProgress,
    RenderStatus,
)

if TYPE_CHECKING:
    from kdenlive_api.client import KdenliveClient


class RenderAPI:
    """Render operations."""

    def __init__(self, client: KdenliveClient) -> None:
        self._client = client

    async def get_presets(self) -> list[RenderPreset]:
        """List available render presets."""
        result = await self._client.call("render.getPresets")
        # Server may return list directly or wrapped in {"presets": [...]}
        presets = result if isinstance(result, list) else result.get("presets", [])
        return [RenderPreset.model_validate(p) for p in presets]

    async def get_preset_info(self, preset_name: str) -> RenderPresetDetail:
        """Get detailed preset information."""
        result = await self._client.call("render.getPresetInfo", {"presetName": preset_name})
        return RenderPresetDetail.model_validate(result)

    async def start(self, preset_name: str, output_path: str) -> RenderJob:
        """Start render job."""
        result = await self._client.call(
            "render.start", {"preset": preset_name, "outputPath": output_path}
        )
        return RenderJob.model_validate(result)

    async def start_with_guides(self, preset_name: str, output_dir: str) -> list[GuideRenderJob]:
        """Render segments between guide markers. Returns list of jobs."""
        result = await self._client.call(
            "render.startWithGuides",
            {"preset": preset_name, "outputDir": output_dir},
        )
        # Server may return list directly or wrapped in {"jobs": [...]}
        jobs = result if isinstance(result, list) else result.get("jobs", [])
        return [GuideRenderJob.model_validate(j) for j in jobs]

    async def stop(self, job_id: str) -> bool:
        """Stop render job."""
        result = await self._client.call("render.stop", {"jobId": job_id})
        return result.get("stopped", False)

    async def stop_all(self) -> int:
        """Stop all render jobs. Returns count stopped."""
        result = await self._client.call("render.stopAll")
        return result.get("count", 0)

    async def get_status(self, job_id: str) -> RenderStatus:
        """Get render job status."""
        result = await self._client.call("render.getStatus", {"jobId": job_id})
        return RenderStatus.model_validate(result)

    async def get_jobs(self) -> list[RenderJob]:
        """List all render jobs."""
        result = await self._client.call("render.getJobs")
        # Server may return list directly or wrapped in {"jobs": [...]}
        jobs = result if isinstance(result, list) else result.get("jobs", [])
        return [RenderJob.model_validate(j) for j in jobs]

    async def get_active_job(self) -> RenderStatus | None:
        """Get currently running job, or None if no job is active."""
        result = await self._client.call("render.getActiveJob")
        if not result or not result.get("jobId"):
            return None
        return RenderStatus.model_validate(result)

    async def set_output(self, default_path: str) -> bool:
        """Set default output path."""
        result = await self._client.call("render.setOutput", {"defaultPath": default_path})
        return result.get("set", False)

    async def watch(self, job_id: str) -> AsyncIterator[RenderProgress]:
        """Watch render progress via notifications.

        Usage:
            async for progress in client.render.watch(job_id):
                print(f"{progress.progress}%")
        """
        import asyncio

        queue: asyncio.Queue[RenderProgress | None] = asyncio.Queue()

        async def handler(method: str, params: dict[str, Any]) -> None:
            if method == "render.progress" and params.get("jobId") == job_id:
                await queue.put(RenderProgress.model_validate(params))
            elif method in ("render.completed", "render.error") and params.get("jobId") == job_id:
                await queue.put(None)  # Signal completion

        self._client.on_notification(handler)

        try:
            while True:
                progress = await queue.get()
                if progress is None:
                    break
                yield progress
        finally:
            # Handler removal would be implemented in client if needed
            pass
