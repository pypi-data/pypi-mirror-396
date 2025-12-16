"""Tests for EffectsAPI."""

from __future__ import annotations

import pytest
from conftest import MockWebSocketServer
from kdenlive_api import KdenliveClient
from kdenlive_api.types import ClipEffect, EffectDetailedInfo, EffectInfo, Keyframe


class TestEffectsListAvailable:
    """Test effects.list_available method."""

    @pytest.mark.asyncio
    async def test_list_available(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test listing available effects."""
        client, server = client_with_server

        server.register_handler(
            "effect.listAvailable",
            {
                "effects": [
                    {
                        "id": "brightness",
                        "name": "Brightness",
                        "category": "video",
                        "description": "Adjust brightness",
                    },
                    {
                        "id": "volume",
                        "name": "Volume",
                        "category": "audio",
                        "description": "Adjust volume",
                    },
                ]
            },
        )

        effects = await client.effects.list_available()

        assert len(effects) == 2
        assert isinstance(effects[0], EffectInfo)
        assert effects[0].id == "brightness"


class TestEffectsGetInfo:
    """Test effects.get_info method."""

    @pytest.mark.asyncio
    async def test_get_info(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting effect info."""
        client, server = client_with_server

        server.register_handler(
            "effect.getInfo",
            {
                "id": "brightness",
                "name": "Brightness",
                "category": "video",
                "description": "Adjust brightness",
                "parameters": [
                    {"name": "level", "type": "double", "min": 0, "max": 2, "default": 1}
                ],
            },
        )

        info = await client.effects.get_info("brightness")

        assert isinstance(info, EffectDetailedInfo)
        assert info.id == "brightness"
        assert len(info.parameters) == 1


class TestEffectsAddRemove:
    """Test effects.add and effects.remove methods."""

    @pytest.mark.asyncio
    async def test_add_effect(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test adding effect to clip."""
        client, server = client_with_server

        server.register_handler("effect.add", {"effectInstanceId": "brightness_0"})

        effect_id = await client.effects.add("brightness", 5)

        assert effect_id == "brightness_0"
        assert server.requests[0]["params"]["effectId"] == "brightness"
        assert server.requests[0]["params"]["clipId"] == 5

    @pytest.mark.asyncio
    async def test_remove_effect(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test removing effect from clip."""
        client, server = client_with_server

        server.register_handler("effect.remove", {"deleted": True})

        result = await client.effects.remove(5, "brightness")

        assert result is True


class TestEffectsGetClipEffects:
    """Test effects.get_clip_effects method."""

    @pytest.mark.asyncio
    async def test_get_clip_effects(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting effects on clip."""
        client, server = client_with_server

        server.register_handler(
            "effect.getClipEffects",
            {"effects": [{"index": 0, "id": "brightness", "name": "Brightness", "enabled": True}]},
        )

        effects = await client.effects.get_clip_effects(5)

        assert len(effects) == 1
        assert isinstance(effects[0], ClipEffect)
        assert effects[0].id == "brightness"


class TestEffectsProperties:
    """Test effect property methods."""

    @pytest.mark.asyncio
    async def test_get_property(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting effect property."""
        client, server = client_with_server

        server.register_handler("effect.getProperty", {"value": 1.2})

        value = await client.effects.get_property(5, "brightness", "level")

        assert value == 1.2

    @pytest.mark.asyncio
    async def test_set_property(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test setting effect property."""
        client, server = client_with_server

        server.register_handler("effect.setProperty", {"updated": True})

        result = await client.effects.set_property(5, "brightness", "level", 1.5)

        assert result is True
        assert server.requests[0]["params"]["value"] == 1.5


class TestEffectsEnableDisable:
    """Test effect enable/disable methods."""

    @pytest.mark.asyncio
    async def test_enable_effect(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test enabling effect."""
        client, server = client_with_server

        server.register_handler("effect.enable", {"enabled": True})

        result = await client.effects.enable(5, "brightness")

        assert result is True

    @pytest.mark.asyncio
    async def test_disable_effect(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test disabling effect."""
        client, server = client_with_server

        server.register_handler("effect.disable", {"enabled": False})

        result = await client.effects.disable(5, "brightness")

        assert result is True


class TestEffectsReorderCopy:
    """Test effect reorder and copy methods."""

    @pytest.mark.asyncio
    async def test_reorder(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test reordering effect."""
        client, server = client_with_server

        server.register_handler("effect.reorder", {"reordered": True})

        result = await client.effects.reorder(5, "brightness", 0)

        assert result is True
        assert server.requests[0]["params"]["newIndex"] == 0

    @pytest.mark.asyncio
    async def test_copy_to_clips(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test copying effect to other clips."""
        client, server = client_with_server

        server.register_handler("effect.copyToClips", {"count": 3})

        result = await client.effects.copy_to_clips(5, "brightness", [6, 7, 8])

        assert result == 3
        assert server.requests[0]["params"]["targetClipIds"] == [6, 7, 8]


class TestEffectsKeyframes:
    """Test keyframe methods."""

    @pytest.mark.asyncio
    async def test_get_keyframes(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test getting keyframes."""
        client, server = client_with_server

        server.register_handler(
            "effect.getKeyframes",
            {
                "keyframes": [
                    {"position": 0, "value": 1.0},
                    {"position": 100, "value": 1.5},
                ]
            },
        )

        keyframes = await client.effects.get_keyframes(5, "brightness", "level")

        assert len(keyframes) == 2
        assert isinstance(keyframes[0], Keyframe)
        assert keyframes[0].position == 0
        assert keyframes[1].value == 1.5

    @pytest.mark.asyncio
    async def test_set_keyframe(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test setting keyframe."""
        client, server = client_with_server

        server.register_handler("effect.setKeyframe", {"set": True})

        result = await client.effects.set_keyframe(5, "brightness", "level", 50, 1.2)

        assert result is True
        assert server.requests[0]["params"]["position"] == 50
        assert server.requests[0]["params"]["value"] == 1.2

    @pytest.mark.asyncio
    async def test_delete_keyframe(
        self, client_with_server: tuple[KdenliveClient, MockWebSocketServer]
    ) -> None:
        """Test deleting keyframe."""
        client, server = client_with_server

        server.register_handler("effect.deleteKeyframe", {"deleted": True})

        result = await client.effects.delete_keyframe(5, "brightness", "level", 50)

        assert result is True
        assert server.requests[0]["params"]["position"] == 50
