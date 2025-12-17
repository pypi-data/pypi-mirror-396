"""Project management API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kdenlive_api.types import ProjectInfo

if TYPE_CHECKING:
    from kdenlive_api.client import KdenliveClient


class ProjectAPI:
    """Project management operations."""

    def __init__(self, client: KdenliveClient) -> None:
        self._client = client

    async def get_info(self) -> ProjectInfo:
        """Get current project information."""
        result = await self._client.call("project.getInfo")
        return ProjectInfo.model_validate(result)

    async def open(self, path: str) -> bool:
        """Open a project file."""
        result = await self._client.call("project.open", {"path": path})
        # Server returns success=true, or empty dict for deferred operations
        return result.get("success", True) if result else True

    async def save(self, path: str | None = None) -> bool:
        """Save current project."""
        params = {"path": path} if path else {}
        result = await self._client.call("project.save", params)
        return result.get("success", True) if result else True

    async def close(self, save_changes: bool = False) -> bool:
        """Close current project.

        Args:
            save_changes: Whether to save changes before closing (default: False).
                         For automation, call save() explicitly before close() if needed.
                         If True and project is modified, auto-saves without prompting.
        """
        result = await self._client.call("project.close", {"saveChanges": save_changes})
        return result.get("success", True) if result else True

    async def new(self, profile: str | None = None) -> bool:
        """Create new project."""
        params = {"profile": profile} if profile else {}
        result = await self._client.call("project.new", params)
        # Server returns empty dict for deferred operations - treat as success
        return result.get("success", True) if result else True

    async def undo(self) -> bool:
        """Undo last action."""
        result = await self._client.call("project.undo")
        return result.get("success", True) if result else True

    async def redo(self) -> bool:
        """Redo last undone action."""
        result = await self._client.call("project.redo")
        return result.get("success", True) if result else True
