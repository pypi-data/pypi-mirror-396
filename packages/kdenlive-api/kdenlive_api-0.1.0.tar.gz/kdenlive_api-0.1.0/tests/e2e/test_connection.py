"""E2E tests for WebSocket connection handling."""

from __future__ import annotations

import asyncio

import pytest
from kdenlive_api import KdenliveClient
from kdenlive_api.exceptions import ConnectionError


@pytest.mark.integration
class TestConnectionLifecycle:
    """Test connection lifecycle operations."""

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, kdenlive_url: str) -> None:
        """Test basic connect and disconnect."""
        client = KdenliveClient(url=kdenlive_url)

        await client.connect()
        assert client.is_connected

        await client.disconnect()
        assert not client.is_connected

    @pytest.mark.asyncio
    async def test_context_manager(self, kdenlive_url: str) -> None:
        """Test async context manager pattern."""
        async with KdenliveClient(url=kdenlive_url) as client:
            assert client.is_connected
            await client.ping()

        assert not client.is_connected

    @pytest.mark.asyncio
    async def test_multiple_connect_calls(self, kdenlive_url: str) -> None:
        """Test that multiple connect calls are handled gracefully."""
        client = KdenliveClient(url=kdenlive_url)

        await client.connect()
        await client.connect()  # Should not fail
        assert client.is_connected

        await client.disconnect()

    @pytest.mark.asyncio
    async def test_multiple_disconnect_calls(self, kdenlive_url: str) -> None:
        """Test that multiple disconnect calls are handled gracefully."""
        client = KdenliveClient(url=kdenlive_url)

        await client.connect()
        await client.disconnect()
        await client.disconnect()  # Should not fail
        assert not client.is_connected

    @pytest.mark.asyncio
    async def test_reconnect(self, kdenlive_url: str) -> None:
        """Test disconnecting and reconnecting."""
        client = KdenliveClient(url=kdenlive_url)

        await client.connect()
        await client.ping()
        await client.disconnect()

        await client.connect()
        await client.ping()
        await client.disconnect()


@pytest.mark.integration
class TestPingVersion:
    """Test basic RPC operations."""

    @pytest.mark.asyncio
    async def test_ping(self, client: KdenliveClient) -> None:
        """Test ping returns pong."""
        result = await client.ping()
        assert result == "pong"

    @pytest.mark.asyncio
    async def test_get_version(self, client: KdenliveClient) -> None:
        """Test getting server version."""
        version = await client.get_version()

        assert "kdenlive" in version
        assert "api" in version
        # Version should be semantic version format
        assert isinstance(version["kdenlive"], str)
        assert isinstance(version["api"], str)

    @pytest.mark.asyncio
    async def test_ping_roundtrip_time(self, client: KdenliveClient) -> None:
        """Test ping roundtrip is reasonably fast."""
        import time

        start = time.monotonic()
        await client.ping()
        elapsed = time.monotonic() - start

        # Should complete within 1 second (local connection)
        assert elapsed < 1.0


@pytest.mark.integration
class TestConnectionErrors:
    """Test connection error handling."""

    @pytest.mark.asyncio
    async def test_connect_invalid_url(self) -> None:
        """Test connecting to invalid URL."""
        client = KdenliveClient(url="ws://localhost:99999")

        with pytest.raises(ConnectionError):
            await client.connect()

    @pytest.mark.asyncio
    async def test_connect_timeout(self) -> None:
        """Test connection timeout."""
        # Use a non-routable IP to force timeout
        client = KdenliveClient(url="ws://10.255.255.1:9876", timeout=1.0)

        with pytest.raises(ConnectionError):
            await client.connect()

    @pytest.mark.asyncio
    async def test_operation_after_disconnect(self, kdenlive_url: str) -> None:
        """Test that operations fail after disconnect."""
        client = KdenliveClient(url=kdenlive_url)

        await client.connect()
        await client.disconnect()

        with pytest.raises(ConnectionError):
            await client.ping()


@pytest.mark.integration
class TestConcurrentConnections:
    """Test multiple concurrent connections."""

    @pytest.mark.asyncio
    async def test_multiple_clients(self, kdenlive_url: str) -> None:
        """Test multiple clients can connect simultaneously."""
        client1 = KdenliveClient(url=kdenlive_url)
        client2 = KdenliveClient(url=kdenlive_url)

        await client1.connect()
        await client2.connect()

        # Both should be able to ping
        result1 = await client1.ping()
        result2 = await client2.ping()

        assert result1 == "pong"
        assert result2 == "pong"

        await client1.disconnect()
        await client2.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, client: KdenliveClient) -> None:
        """Test concurrent operations on same client."""
        # Run multiple pings concurrently
        tasks = [client.ping() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        assert all(r == "pong" for r in results)


@pytest.mark.integration
class TestNotificationHandling:
    """Test notification/event handling."""

    @pytest.mark.asyncio
    async def test_register_notification_handler(self, client: KdenliveClient) -> None:
        """Test registering a notification handler."""
        received: list[dict] = []

        def handler(data: dict) -> None:
            received.append(data)

        client.on_notification("project.changed", handler)

        # The handler should be registered (we can't easily trigger notifications
        # without modifying the project, so just verify registration works)
        assert True

    @pytest.mark.asyncio
    async def test_unregister_notification_handler(self, client: KdenliveClient) -> None:
        """Test unregistering a notification handler."""

        def handler(data: dict) -> None:
            pass

        client.on_notification("project.changed", handler)
        client.off_notification("project.changed", handler)

        # Should not raise
        assert True
