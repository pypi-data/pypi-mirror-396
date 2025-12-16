"""Pytest fixtures for kdenlive-api tests."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from kdenlive_api import KdenliveClient


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_client() -> AsyncGenerator[KdenliveClient, None]:
    """Create a client in mock mode."""
    client = KdenliveClient(mock=True)
    await client.connect()
    yield client
    await client.disconnect()


@pytest_asyncio.fixture
async def mock_ws_client() -> AsyncGenerator[KdenliveClient, None]:
    """Create a client with mocked WebSocket."""
    client = KdenliveClient(mock=False)

    # Mock WebSocket
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.close = AsyncMock()

    # Track request IDs for responses
    responses: dict[int, dict[str, Any]] = {}

    async def mock_connect(url: str) -> AsyncMock:
        return mock_ws

    def set_response(request_id: int, result: dict[str, Any]) -> None:
        responses[request_id] = {"jsonrpc": "2.0", "result": result, "id": request_id}

    # Patch websockets.connect
    with patch("websockets.connect", mock_connect):
        await client.connect()

        # Helper to simulate responses
        client._test_set_response = set_response  # type: ignore[attr-defined]
        client._test_ws = mock_ws  # type: ignore[attr-defined]

        yield client

    await client.disconnect()


class MockWebSocketServer:
    """Mock WebSocket server for testing."""

    def __init__(self) -> None:
        self.handlers: dict[str, Any] = {}
        self.requests: list[dict[str, Any]] = []

    def register_handler(self, method: str, response: Any) -> None:
        """Register a response for a method."""
        self.handlers[method] = response

    def get_response(self, request: dict[str, Any]) -> dict[str, Any]:
        """Get response for a request."""
        self.requests.append(request)
        method = request.get("method", "")
        request_id = request.get("id")

        if method in self.handlers:
            result = self.handlers[method]
            if callable(result):
                result = result(request.get("params", {}))
            return {"jsonrpc": "2.0", "result": result, "id": request_id}

        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Method not found: {method}"},
            "id": request_id,
        }


@pytest.fixture
def mock_server() -> MockWebSocketServer:
    """Create a mock WebSocket server."""
    server = MockWebSocketServer()

    # Register default responses
    server.register_handler("rpc.ping", {"pong": True})
    server.register_handler("rpc.getVersion", {"kdenlive": "25.04.0", "rpc": "1.0.0"})
    server.register_handler(
        "project.getInfo",
        {
            "path": "/test/project.kdenlive",
            "name": "Test Project",
            "profile": "atsc_1080p_25",
            "fps": 25.0,
            "width": 1920,
            "height": 1080,
            "duration": 7500,
            "modified": False,
        },
    )
    server.register_handler(
        "timeline.getInfo",
        {
            "duration": 7500,
            "trackCount": 4,
            "videoTracks": 2,
            "audioTracks": 2,
            "position": 0,
        },
    )
    server.register_handler(
        "timeline.getTracks",
        {
            "tracks": [
                {
                    "id": 1,
                    "name": "Video 1",
                    "type": "video",
                    "locked": False,
                    "muted": False,
                    "hidden": False,
                },
                {
                    "id": 2,
                    "name": "Video 2",
                    "type": "video",
                    "locked": False,
                    "muted": False,
                    "hidden": False,
                },
                {
                    "id": 3,
                    "name": "Audio 1",
                    "type": "audio",
                    "locked": False,
                    "muted": False,
                    "hidden": False,
                },
                {
                    "id": 4,
                    "name": "Audio 2",
                    "type": "audio",
                    "locked": False,
                    "muted": False,
                    "hidden": False,
                },
            ]
        },
    )
    server.register_handler(
        "timeline.getClips",
        {
            "clips": [
                {
                    "id": 1,
                    "binId": "clip1",
                    "trackId": 1,
                    "position": 0,
                    "duration": 250,
                    "in": 0,
                    "out": 250,
                    "name": "test_clip.mp4",
                }
            ]
        },
    )
    server.register_handler("bin.listClips", {"clips": []})
    server.register_handler("bin.listFolders", {"folders": []})
    server.register_handler("effect.listAvailable", {"effects": []})
    server.register_handler("render.getPresets", {"presets": []})

    return server


@pytest_asyncio.fixture
async def client_with_server(
    mock_server: MockWebSocketServer,
) -> AsyncGenerator[tuple[KdenliveClient, MockWebSocketServer], None]:
    """Create client connected to mock server."""
    client = KdenliveClient(mock=False)

    # Create mock WebSocket that uses the server
    mock_ws = AsyncMock()
    sent_messages: list[str] = []

    async def mock_send(message: str) -> None:
        sent_messages.append(message)
        request = json.loads(message)
        response = mock_server.get_response(request)

        # Simulate receiving response
        request_id = request.get("id")
        if request_id in client._pending:
            future = client._pending[request_id]
            if not future.done():
                future.set_result(response)

    mock_ws.send = mock_send
    mock_ws.close = AsyncMock()

    async def mock_connect(url: str) -> AsyncMock:
        return mock_ws

    with patch("websockets.connect", mock_connect):
        await client.connect()
        yield client, mock_server

    await client.disconnect()
