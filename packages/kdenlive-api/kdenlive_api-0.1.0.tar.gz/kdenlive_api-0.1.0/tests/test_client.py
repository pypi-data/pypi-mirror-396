"""Tests for KdenliveClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from kdenlive_api import KdenliveClient
from kdenlive_api.exceptions import ConnectionError


class TestClientConnection:
    """Test client connection handling."""

    @pytest.mark.asyncio
    async def test_mock_mode_connect(self) -> None:
        """Test connecting in mock mode."""
        client = KdenliveClient(mock=True)
        await client.connect()

        assert client._connected.is_set()

        await client.disconnect()
        assert not client._connected.is_set()

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager."""
        async with KdenliveClient(mock=True) as client:
            assert client._connected.is_set()

        assert not client._connected.is_set()

    @pytest.mark.asyncio
    async def test_connection_failure(self) -> None:
        """Test connection failure handling."""
        client = KdenliveClient(url="ws://invalid:9999", reconnect=False)

        with pytest.raises(ConnectionError):
            await client.connect()

    @pytest.mark.asyncio
    async def test_websocket_connect(self) -> None:
        """Test WebSocket connection."""
        mock_ws = AsyncMock()

        async def mock_connect(url: str) -> AsyncMock:
            return mock_ws

        client = KdenliveClient()

        with patch("websockets.connect", mock_connect):
            await client.connect()
            assert client._connected.is_set()
            assert client._ws is mock_ws

        await client.disconnect()


class TestClientMockMode:
    """Test mock mode responses."""

    @pytest.mark.asyncio
    async def test_ping(self, mock_client: KdenliveClient) -> None:
        """Test ping in mock mode."""
        result = await mock_client.ping()
        assert result is True

    @pytest.mark.asyncio
    async def test_get_version(self, mock_client: KdenliveClient) -> None:
        """Test get_version in mock mode."""
        version = await mock_client.get_version()
        assert "kdenlive" in version
        assert "rpc" in version

    @pytest.mark.asyncio
    async def test_mock_project_info(self, mock_client: KdenliveClient) -> None:
        """Test project.getInfo in mock mode."""
        result = await mock_client.call("project.getInfo")
        assert result["name"] == "Mock Project"
        assert result["width"] == 1920
        assert result["height"] == 1080

    @pytest.mark.asyncio
    async def test_mock_timeline_info(self, mock_client: KdenliveClient) -> None:
        """Test timeline.getInfo in mock mode."""
        result = await mock_client.call("timeline.getInfo")
        assert result["trackCount"] == 4
        assert result["videoTracks"] == 2
        assert result["audioTracks"] == 2


class TestClientNamespaces:
    """Test API namespace properties."""

    @pytest.mark.asyncio
    async def test_project_namespace(self, mock_client: KdenliveClient) -> None:
        """Test project namespace is accessible."""
        assert mock_client.project is not None
        # Verify lazy initialization
        assert mock_client._project is not None

    @pytest.mark.asyncio
    async def test_timeline_namespace(self, mock_client: KdenliveClient) -> None:
        """Test timeline namespace is accessible."""
        assert mock_client.timeline is not None
        assert mock_client._timeline is not None

    @pytest.mark.asyncio
    async def test_bin_namespace(self, mock_client: KdenliveClient) -> None:
        """Test bin namespace is accessible."""
        assert mock_client.bin is not None
        assert mock_client._bin is not None

    @pytest.mark.asyncio
    async def test_effects_namespace(self, mock_client: KdenliveClient) -> None:
        """Test effects namespace is accessible."""
        assert mock_client.effects is not None
        assert mock_client._effects is not None

    @pytest.mark.asyncio
    async def test_render_namespace(self, mock_client: KdenliveClient) -> None:
        """Test render namespace is accessible."""
        assert mock_client.render is not None
        assert mock_client._render is not None

    @pytest.mark.asyncio
    async def test_asset_namespace(self, mock_client: KdenliveClient) -> None:
        """Test asset namespace is accessible."""
        assert mock_client.asset is not None
        assert mock_client._asset is not None

    @pytest.mark.asyncio
    async def test_transition_namespace(self, mock_client: KdenliveClient) -> None:
        """Test transition namespace is accessible."""
        assert mock_client.transition is not None
        assert mock_client._transition is not None

    @pytest.mark.asyncio
    async def test_composition_namespace(self, mock_client: KdenliveClient) -> None:
        """Test composition namespace is accessible."""
        assert mock_client.composition is not None
        assert mock_client._composition is not None


class TestNotificationHandling:
    """Test notification handler registration."""

    @pytest.mark.asyncio
    async def test_register_handler(self, mock_client: KdenliveClient) -> None:
        """Test registering notification handler."""
        received: list[tuple[str, dict]] = []

        async def handler(method: str, params: dict) -> None:
            received.append((method, params))

        mock_client.on_notification(handler)
        assert len(mock_client._notification_handlers) == 1

    @pytest.mark.asyncio
    async def test_handle_notification(self, mock_client: KdenliveClient) -> None:
        """Test notification handling."""
        received: list[tuple[str, dict]] = []

        async def handler(method: str, params: dict) -> None:
            received.append((method, params))

        mock_client.on_notification(handler)

        # Simulate receiving a notification
        notification = '{"jsonrpc": "2.0", "method": "render.progress", "params": {"progress": 50}}'
        await mock_client._handle_message(notification)

        assert len(received) == 1
        assert received[0][0] == "render.progress"
        assert received[0][1]["progress"] == 50


class TestClientConfiguration:
    """Test client configuration options."""

    def test_default_url(self) -> None:
        """Test default WebSocket URL."""
        client = KdenliveClient()
        assert client.url == "ws://localhost:9876"

    def test_custom_url(self) -> None:
        """Test custom WebSocket URL."""
        client = KdenliveClient(url="ws://192.168.1.100:9876")
        assert client.url == "ws://192.168.1.100:9876"

    def test_reconnect_settings(self) -> None:
        """Test reconnect configuration."""
        client = KdenliveClient(reconnect=False, reconnect_delay=5.0)
        assert client.reconnect is False
        assert client.reconnect_delay == 5.0

    def test_mock_mode_setting(self) -> None:
        """Test mock mode configuration."""
        client = KdenliveClient(mock=True)
        assert client.mock is True
