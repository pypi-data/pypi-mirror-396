"""Pytest fixtures for e2e integration tests.

These tests require a running Kdenlive instance with the WebSocket server enabled.
Run with: pytest -m integration
Skip with: pytest -m "not integration"
"""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from kdenlive_api import KdenliveClient

# Environment variables for configuration
KDENLIVE_WS_URL = os.environ.get("KDENLIVE_WS_URL", "ws://localhost:9876")
KDENLIVE_TEST_TIMEOUT = int(os.environ.get("KDENLIVE_TEST_TIMEOUT", "30"))
KDENLIVE_SKIP_SLOW = os.environ.get("KDENLIVE_SKIP_SLOW", "").lower() == "true"


def is_kdenlive_available() -> bool:
    """Check if Kdenlive WebSocket server is available."""

    async def check() -> bool:
        try:
            client = KdenliveClient(url=KDENLIVE_WS_URL, timeout=5.0)
            await client.connect()
            await client.ping()
            await client.disconnect()
            return True
        except Exception:
            return False

    return asyncio.run(check())


# Skip all integration tests if Kdenlive is not available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not is_kdenlive_available(),
        reason="Kdenlive WebSocket server not available",
    ),
]


@pytest.fixture(scope="session")
def kdenlive_url() -> str:
    """Get the Kdenlive WebSocket URL."""
    return KDENLIVE_WS_URL


@pytest.fixture(scope="session")
def test_timeout() -> int:
    """Get the test timeout in seconds."""
    return KDENLIVE_TEST_TIMEOUT


@pytest_asyncio.fixture
async def client(kdenlive_url: str) -> AsyncGenerator[KdenliveClient, None]:
    """Create a connected Kdenlive client for testing.

    This fixture provides a fresh client connection for each test.
    The client is automatically disconnected after the test.
    """
    client = KdenliveClient(url=kdenlive_url)
    await client.connect()
    yield client
    await client.disconnect()


@pytest_asyncio.fixture
async def client_with_empty_project(
    client: KdenliveClient,
) -> AsyncGenerator[KdenliveClient, None]:
    """Provide a client with a new empty project.

    Creates a new project before the test and closes it after.
    """
    await client.project.new()
    yield client
    await client.project.close(save_changes=False)


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    tmp = Path(tempfile.mkdtemp(prefix="kdenlive_test_"))
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def test_project_path(temp_dir: Path) -> Path:
    """Get a path for a test project file."""
    return temp_dir / "test_project.kdenlive"


@pytest.fixture
def test_output_path(temp_dir: Path) -> Path:
    """Get a path for test render output."""
    return temp_dir / "output.mp4"


@pytest.fixture(scope="session")
def sample_video_path() -> Path | None:
    """Get path to a sample video file for testing.

    Set KDENLIVE_TEST_VIDEO environment variable to provide a video file.
    Returns None if no sample video is configured.
    """
    video_path = os.environ.get("KDENLIVE_TEST_VIDEO")
    if video_path and Path(video_path).exists():
        return Path(video_path)
    return None


@pytest.fixture(scope="session")
def sample_audio_path() -> Path | None:
    """Get path to a sample audio file for testing.

    Set KDENLIVE_TEST_AUDIO environment variable to provide an audio file.
    Returns None if no sample audio is configured.
    """
    audio_path = os.environ.get("KDENLIVE_TEST_AUDIO")
    if audio_path and Path(audio_path).exists():
        return Path(audio_path)
    return None


@pytest.fixture(scope="session")
def sample_image_path() -> Path | None:
    """Get path to a sample image file for testing.

    Set KDENLIVE_TEST_IMAGE environment variable to provide an image file.
    Returns None if no sample image is configured.
    """
    image_path = os.environ.get("KDENLIVE_TEST_IMAGE")
    if image_path and Path(image_path).exists():
        return Path(image_path)
    return None


def skip_without_sample_video(sample_video_path: Path | None) -> None:
    """Skip test if no sample video is available."""
    if sample_video_path is None:
        pytest.skip("No sample video configured (set KDENLIVE_TEST_VIDEO)")


def skip_without_sample_audio(sample_audio_path: Path | None) -> None:
    """Skip test if no sample audio is available."""
    if sample_audio_path is None:
        pytest.skip("No sample audio configured (set KDENLIVE_TEST_AUDIO)")


def skip_slow_tests() -> None:
    """Skip slow tests when KDENLIVE_SKIP_SLOW is set."""
    if KDENLIVE_SKIP_SLOW:
        pytest.skip("Slow tests disabled (KDENLIVE_SKIP_SLOW=true)")
