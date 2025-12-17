"""Kdenlive WebSocket JSON-RPC client."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

import websockets
from websockets.client import WebSocketClientProtocol

from kdenlive_api.exceptions import ConnectionError, raise_for_error

# Environment variable names
KDENLIVE_WS_URL_ENV = "KDENLIVE_WS_URL"
KDENLIVE_AUTH_TOKEN_ENV = "KDENLIVE_AUTH_TOKEN"

# Default values
DEFAULT_WS_URL = "ws://localhost:9876"

if TYPE_CHECKING:
    from kdenlive_api.asset import AssetAPI
    from kdenlive_api.bin import BinAPI
    from kdenlive_api.composition import CompositionAPI
    from kdenlive_api.effects import EffectsAPI
    from kdenlive_api.project import ProjectAPI
    from kdenlive_api.render import RenderAPI
    from kdenlive_api.timeline import TimelineAPI
    from kdenlive_api.transition import TransitionAPI


NotificationHandler = Callable[[str, dict[str, Any]], Awaitable[None]]


class KdenliveClient:
    """Async client for Kdenlive JSON-RPC API.

    Usage:
        async with KdenliveClient() as client:
            info = await client.project.get_info()
            print(info.name)
    """

    def __init__(
        self,
        url: str | None = None,
        *,
        auth_token: str | None = None,
        mock: bool = False,
        reconnect: bool = True,
        reconnect_delay: float = 1.0,
    ) -> None:
        """Initialize Kdenlive client.

        Args:
            url: WebSocket URL to connect to. Defaults to KDENLIVE_WS_URL env var
                 or ws://localhost:9876
            auth_token: Bearer token for authentication. Defaults to KDENLIVE_AUTH_TOKEN
                        env var if set
            mock: If True, use mock mode (no real connection)
            reconnect: If True, automatically reconnect on disconnect
            reconnect_delay: Seconds to wait before reconnecting

        Environment Variables:
            KDENLIVE_WS_URL: WebSocket URL (default: ws://localhost:9876)
            KDENLIVE_AUTH_TOKEN: Bearer token for authentication
        """
        self.url = url or os.environ.get(KDENLIVE_WS_URL_ENV, DEFAULT_WS_URL)
        self.auth_token = auth_token or os.environ.get(KDENLIVE_AUTH_TOKEN_ENV)
        self.mock = mock
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay

        self._ws: WebSocketClientProtocol | None = None
        self._request_id = 0
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._notification_handlers: list[NotificationHandler] = []
        self._receive_task: asyncio.Task[None] | None = None
        self._connected = asyncio.Event()

        # API namespaces (lazy initialized)
        self._project: ProjectAPI | None = None
        self._timeline: TimelineAPI | None = None
        self._bin: BinAPI | None = None
        self._effects: EffectsAPI | None = None
        self._render: RenderAPI | None = None
        self._asset: AssetAPI | None = None
        self._transition: TransitionAPI | None = None
        self._composition: CompositionAPI | None = None

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to Kdenlive."""
        return self._connected.is_set() and (self.mock or self._ws is not None)

    @property
    def project(self) -> ProjectAPI:
        """Project management API."""
        if self._project is None:
            from kdenlive_api.project import ProjectAPI

            self._project = ProjectAPI(self)
        return self._project

    @property
    def timeline(self) -> TimelineAPI:
        """Timeline operations API."""
        if self._timeline is None:
            from kdenlive_api.timeline import TimelineAPI

            self._timeline = TimelineAPI(self)
        return self._timeline

    @property
    def bin(self) -> BinAPI:
        """Bin/clip management API."""
        if self._bin is None:
            from kdenlive_api.bin import BinAPI

            self._bin = BinAPI(self)
        return self._bin

    @property
    def effects(self) -> EffectsAPI:
        """Effects API."""
        if self._effects is None:
            from kdenlive_api.effects import EffectsAPI

            self._effects = EffectsAPI(self)
        return self._effects

    @property
    def render(self) -> RenderAPI:
        """Render API."""
        if self._render is None:
            from kdenlive_api.render import RenderAPI

            self._render = RenderAPI(self)
        return self._render

    @property
    def asset(self) -> AssetAPI:
        """Asset discovery API."""
        if self._asset is None:
            from kdenlive_api.asset import AssetAPI

            self._asset = AssetAPI(self)
        return self._asset

    @property
    def transition(self) -> TransitionAPI:
        """Transition API."""
        if self._transition is None:
            from kdenlive_api.transition import TransitionAPI

            self._transition = TransitionAPI(self)
        return self._transition

    @property
    def composition(self) -> CompositionAPI:
        """Composition API."""
        if self._composition is None:
            from kdenlive_api.composition import CompositionAPI

            self._composition = CompositionAPI(self)
        return self._composition

    async def connect(self) -> None:
        """Connect to Kdenlive WebSocket server."""
        if self.mock:
            self._connected.set()
            return

        try:
            # Build additional headers for authentication
            extra_headers: dict[str, str] = {}
            if self.auth_token:
                extra_headers["Authorization"] = f"Bearer {self.auth_token}"

            self._ws = await websockets.connect(
                self.url,
                additional_headers=extra_headers if extra_headers else None,
            )
            self._connected.set()
            self._receive_task = asyncio.create_task(self._receive_loop())
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.url}: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from Kdenlive."""
        self._connected.clear()

        if self._receive_task:
            self._receive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._receive_task
            self._receive_task = None

        if self._ws:
            await self._ws.close()
            self._ws = None

        # Cancel any pending requests
        for future in self._pending.values():
            future.cancel()
        self._pending.clear()

    async def __aenter__(self) -> KdenliveClient:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.disconnect()

    def on_notification(self, handler: NotificationHandler) -> None:
        """Register a notification handler.

        Args:
            handler: Async function(method: str, params: dict) to call on notification
        """
        self._notification_handlers.append(handler)

    async def call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        request_timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Make a JSON-RPC call.

        Args:
            method: Method name (e.g., "project.getInfo")
            params: Method parameters
            request_timeout: Request timeout in seconds

        Returns:
            Result from the RPC call

        Raises:
            KdenliveError: On RPC error
            asyncio.TimeoutError: On timeout
        """
        if self.mock:
            return await self._mock_call(method, params or {})

        if not self._ws:
            raise ConnectionError("Not connected to Kdenlive")

        self._request_id += 1
        request_id = self._request_id

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id,
        }

        future: asyncio.Future[dict[str, Any]] = asyncio.get_event_loop().create_future()
        self._pending[request_id] = future

        try:
            await self._ws.send(json.dumps(request))
            response = await asyncio.wait_for(future, timeout=request_timeout)
        finally:
            self._pending.pop(request_id, None)

        if "error" in response:
            error = response["error"]
            raise_for_error(error.get("code", -32603), error.get("message", "Unknown error"))

        return response.get("result", {})

    async def _receive_loop(self) -> None:
        """Background task to receive messages."""
        assert self._ws is not None

        try:
            async for message in self._ws:
                await self._handle_message(message)
        except websockets.ConnectionClosed:
            self._connected.clear()
            if self.reconnect:
                asyncio.create_task(self._reconnect())

    async def _handle_message(self, message: str | bytes) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return

        # Check if it's a response (has id)
        if "id" in data and data["id"] in self._pending:
            future = self._pending.get(data["id"])
            if future and not future.done():
                future.set_result(data)
            return

        # It's a notification
        method = data.get("method", "")
        params = data.get("params", {})

        for handler in self._notification_handlers:
            with contextlib.suppress(Exception):
                await handler(method, params)

    async def _reconnect(self) -> None:
        """Attempt to reconnect after disconnect."""
        while self.reconnect and not self._connected.is_set():
            await asyncio.sleep(self.reconnect_delay)
            try:
                await self.connect()
            except ConnectionError:
                continue

    async def _mock_call(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Handle mock mode calls."""
        # Return mock responses based on method
        mock_responses: dict[str, dict[str, Any]] = {
            "rpc.ping": {"pong": True},
            "rpc.getVersion": {"kdenlive": "25.04.0", "rpc": "1.0.0"},
            "project.getInfo": {
                "path": "/mock/project.kdenlive",
                "name": "Mock Project",
                "profile": "atsc_1080p_25",
                "fps": 25.0,
                "width": 1920,
                "height": 1080,
                "duration": 7500,
                "modified": False,
            },
            "timeline.getInfo": {
                "duration": 7500,
                "trackCount": 4,
                "videoTracks": 2,
                "audioTracks": 2,
                "position": 0,
            },
            "bin.listClips": {"clips": []},
            "render.getPresets": {"presets": []},
        }

        return mock_responses.get(method, {})

    async def ping(self) -> bool:
        """Ping the server.

        Returns:
            True if server responded
        """
        result = await self.call("rpc.ping")
        return result.get("pong", False)

    async def get_version(self) -> dict[str, str]:
        """Get server version info.

        Returns:
            Dict with 'kdenlive' and 'rpc' version strings
        """
        return await self.call("rpc.getVersion")
