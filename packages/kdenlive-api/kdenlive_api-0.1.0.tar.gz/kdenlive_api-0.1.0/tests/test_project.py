"""Tests for ProjectAPI."""

from __future__ import annotations

import pytest
from conftest import MockWebSocketServer
from kdenlive_api import KdenliveClient
from kdenlive_api.types import ProjectInfo


class TestProjectGetInfo:
    """Test project.get_info method."""

    @pytest.mark.asyncio
    async def test_get_info_mock(self, mock_client: KdenliveClient) -> None:
        """Test get_info in mock mode."""
        info = await mock_client.project.get_info()

        assert isinstance(info, ProjectInfo)
        assert info.name == "Mock Project"
        assert info.width == 1920
        assert info.height == 1080
        assert info.fps == 25.0

    @pytest.mark.asyncio
    async def test_get_info_with_server(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test get_info with mock server."""
        client, server = client_with_server

        info = await client.project.get_info()

        assert isinstance(info, ProjectInfo)
        assert info.name == "Test Project"
        assert info.path == "/test/project.kdenlive"
        assert info.profile == "atsc_1080p_25"


class TestProjectOpen:
    """Test project.open method."""

    @pytest.mark.asyncio
    async def test_open_project(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test opening a project."""
        client, server = client_with_server

        server.register_handler("project.open", {"success": True})

        result = await client.project.open("/path/to/project.kdenlive")

        assert result is True
        assert len(server.requests) == 1
        assert server.requests[0]["params"]["path"] == "/path/to/project.kdenlive"


class TestProjectSave:
    """Test project.save method."""

    @pytest.mark.asyncio
    async def test_save_project(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test saving a project."""
        client, server = client_with_server

        server.register_handler("project.save", {"success": True, "path": "/test/project.kdenlive"})

        result = await client.project.save()

        assert result is True

    @pytest.mark.asyncio
    async def test_save_as_project(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test Save As functionality."""
        client, server = client_with_server

        server.register_handler("project.save", {"success": True, "path": "/new/path.kdenlive"})

        result = await client.project.save("/new/path.kdenlive")

        assert result is True
        assert server.requests[0]["params"]["path"] == "/new/path.kdenlive"


class TestProjectClose:
    """Test project.close method."""

    @pytest.mark.asyncio
    async def test_close_project(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test closing a project."""
        client, server = client_with_server

        server.register_handler("project.close", {"success": True})

        result = await client.project.close()

        assert result is True

    @pytest.mark.asyncio
    async def test_close_with_save(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test closing with save_changes=True."""
        client, server = client_with_server

        server.register_handler("project.close", {"success": True})

        result = await client.project.close(save_changes=True)

        assert result is True
        assert server.requests[0]["params"]["saveChanges"] is True


class TestProjectNew:
    """Test project.new method."""

    @pytest.mark.asyncio
    async def test_new_project(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test creating a new project."""
        client, server = client_with_server

        server.register_handler("project.new", {"success": True})

        result = await client.project.new()

        assert result is True

    @pytest.mark.asyncio
    async def test_new_project_with_profile(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test creating a new project with profile."""
        client, server = client_with_server

        server.register_handler("project.new", {"success": True})

        result = await client.project.new(profile="atsc_1080p_30")

        assert result is True
        assert server.requests[0]["params"]["profile"] == "atsc_1080p_30"


class TestProjectUndoRedo:
    """Test project.undo and project.redo methods."""

    @pytest.mark.asyncio
    async def test_undo(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test undo action."""
        client, server = client_with_server

        server.register_handler("project.undo", {"success": True, "action": "Insert clip"})

        result = await client.project.undo()

        assert result is True

    @pytest.mark.asyncio
    async def test_redo(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test redo action."""
        client, server = client_with_server

        server.register_handler("project.redo", {"success": True, "action": "Insert clip"})

        result = await client.project.redo()

        assert result is True
