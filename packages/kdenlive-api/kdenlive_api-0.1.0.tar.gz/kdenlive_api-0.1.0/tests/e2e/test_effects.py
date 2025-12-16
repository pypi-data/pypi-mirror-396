"""E2E tests for effects operations."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import skip_without_sample_video
from kdenlive_api import KdenliveClient
from kdenlive_api.types import ClipEffect, EffectDetailedInfo, EffectInfo


@pytest.mark.integration
class TestEffectsList:
    """Test listing available effects."""

    @pytest.mark.asyncio
    async def test_list_available_effects(self, client: KdenliveClient) -> None:
        """Test getting list of available effects."""
        effects = await client.effects.list_available()

        assert isinstance(effects, list)
        assert len(effects) > 0
        assert all(isinstance(e, EffectInfo) for e in effects)

    @pytest.mark.asyncio
    async def test_effects_have_categories(self, client: KdenliveClient) -> None:
        """Test that effects have categories."""
        effects = await client.effects.list_available()

        categories = {e.category for e in effects}
        # Should have both video and audio effects
        assert len(categories) > 0


@pytest.mark.integration
class TestEffectInfo:
    """Test getting effect information."""

    @pytest.mark.asyncio
    async def test_get_effect_info(self, client: KdenliveClient) -> None:
        """Test getting detailed effect info."""
        # Get list first to find a valid effect ID
        effects = await client.effects.list_available()
        assert len(effects) > 0

        effect_id = effects[0].id
        info = await client.effects.get_info(effect_id)

        assert isinstance(info, EffectDetailedInfo)
        assert info.id == effect_id
        assert info.name == effects[0].name

    @pytest.mark.asyncio
    async def test_effect_has_parameters(self, client: KdenliveClient) -> None:
        """Test that effects have parameter definitions."""
        effects = await client.effects.list_available()

        # Find an effect that typically has parameters (like brightness)
        brightness = next(
            (e for e in effects if "brightness" in e.name.lower()),
            effects[0],
        )

        info = await client.effects.get_info(brightness.id)

        assert isinstance(info.parameters, list)
        # Most effects have at least one parameter
        if len(info.parameters) > 0:
            param = info.parameters[0]
            assert param.name
            assert param.type


@pytest.mark.integration
class TestEffectAddRemove:
    """Test adding and removing effects from clips."""

    @pytest.mark.asyncio
    async def test_add_effect_to_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test adding an effect to a timeline clip."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Import and add clip to timeline
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Get an effect to add
        effects = await client.effects.list_available()
        effect = next(
            (e for e in effects if e.category == "video"),
            effects[0],
        )

        # Add effect
        effect_instance_id = await client.effects.add(effect.id, timeline_clip_id)

        assert isinstance(effect_instance_id, str)
        assert len(effect_instance_id) > 0

    @pytest.mark.asyncio
    async def test_remove_effect_from_clip(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test removing an effect from a clip."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup: add clip with effect
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, timeline_clip_id)

        # Remove the effect
        result = await client.effects.remove(timeline_clip_id, effect.id)
        assert result is True

        # Verify it's gone
        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)
        assert not any(e.id == effect.id for e in clip_effects)


@pytest.mark.integration
class TestEffectGetClipEffects:
    """Test getting effects on a clip."""

    @pytest.mark.asyncio
    async def test_get_clip_effects_empty(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test getting effects from clip with no effects."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)

        assert isinstance(clip_effects, list)
        assert len(clip_effects) == 0

    @pytest.mark.asyncio
    async def test_get_clip_effects_with_effects(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test getting effects from clip with effects added."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Add clip and effect
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, timeline_clip_id)

        # Get effects
        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)

        assert len(clip_effects) >= 1
        assert isinstance(clip_effects[0], ClipEffect)


@pytest.mark.integration
class TestEffectProperties:
    """Test effect property operations."""

    @pytest.mark.asyncio
    async def test_get_effect_property(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test getting an effect property value."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup clip with effect
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        # Find an effect with parameters
        effects = await client.effects.list_available()
        effect = next(
            (e for e in effects if e.category == "video"),
            effects[0],
        )
        await client.effects.add(effect.id, timeline_clip_id)

        # Get effect info to find a parameter
        info = await client.effects.get_info(effect.id)
        if info.parameters:
            param = info.parameters[0]
            value = await client.effects.get_property(
                timeline_clip_id,
                effect.id,
                param.name,
            )
            # Value should exist (might be default value)
            assert value is not None

    @pytest.mark.asyncio
    async def test_set_effect_property(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test setting an effect property value."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup clip with effect
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        effect = next(
            (e for e in effects if e.category == "video"),
            effects[0],
        )
        await client.effects.add(effect.id, timeline_clip_id)

        # Get effect info to find a settable parameter
        info = await client.effects.get_info(effect.id)
        if info.parameters:
            param = info.parameters[0]
            # Set a new value (try middle of range if available)
            new_value = param.default if param.default is not None else 0.5

            result = await client.effects.set_property(
                timeline_clip_id,
                effect.id,
                param.name,
                new_value,
            )
            assert result is True


@pytest.mark.integration
class TestEffectEnableDisable:
    """Test enabling/disabling effects."""

    @pytest.mark.asyncio
    async def test_disable_effect(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test disabling an effect."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup clip with effect
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, timeline_clip_id)

        # Disable
        result = await client.effects.disable(timeline_clip_id, effect.id)
        assert result is True

        # Verify disabled
        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)
        clip_effect = next(e for e in clip_effects if e.id == effect.id)
        assert clip_effect.enabled is False

    @pytest.mark.asyncio
    async def test_enable_effect(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test enabling a disabled effect."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup clip with effect
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, timeline_clip_id)

        # Disable then enable
        await client.effects.disable(timeline_clip_id, effect.id)
        result = await client.effects.enable(timeline_clip_id, effect.id)
        assert result is True

        # Verify enabled
        clip_effects = await client.effects.get_clip_effects(timeline_clip_id)
        clip_effect = next(e for e in clip_effects if e.id == effect.id)
        assert clip_effect.enabled is True


@pytest.mark.integration
class TestEffectReorder:
    """Test reordering effects on a clip."""

    @pytest.mark.asyncio
    async def test_reorder_effects(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test reordering effects on a clip."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup clip with multiple effects
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        video_effects = [e for e in effects if e.category == "video"][:2]

        if len(video_effects) < 2:
            pytest.skip("Need at least 2 video effects for reorder test")

        # Add two effects
        await client.effects.add(video_effects[0].id, timeline_clip_id)
        await client.effects.add(video_effects[1].id, timeline_clip_id)

        # Reorder - move second effect to first position
        result = await client.effects.reorder(
            timeline_clip_id,
            video_effects[1].id,
            new_index=0,
        )
        assert result is True


@pytest.mark.integration
class TestEffectCopy:
    """Test copying effects between clips."""

    @pytest.mark.asyncio
    async def test_copy_effect_to_clips(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test copying an effect to other clips."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup multiple clips
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")

        clip_info = await client.bin.get_clip_info(clip_id)
        duration = clip_info.duration

        source_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )
        target_clip1_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=duration,
        )
        target_clip2_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=duration * 2,
        )

        # Add effect to source
        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, source_clip_id)

        # Copy to targets
        count = await client.effects.copy_to_clips(
            source_clip_id,
            effect.id,
            [target_clip1_id, target_clip2_id],
        )
        assert count == 2

        # Verify targets have the effect
        effects1 = await client.effects.get_clip_effects(target_clip1_id)
        effects2 = await client.effects.get_clip_effects(target_clip2_id)
        assert any(e.id == effect.id for e in effects1)
        assert any(e.id == effect.id for e in effects2)


@pytest.mark.integration
class TestEffectKeyframes:
    """Test keyframe operations."""

    @pytest.mark.asyncio
    async def test_get_keyframes_empty(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test getting keyframes when none set."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup clip with effect
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, timeline_clip_id)

        info = await client.effects.get_info(effect.id)
        if info.parameters:
            keyframes = await client.effects.get_keyframes(
                timeline_clip_id,
                effect.id,
                info.parameters[0].name,
            )
            assert isinstance(keyframes, list)

    @pytest.mark.asyncio
    async def test_set_keyframe(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test setting a keyframe."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup clip with effect
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, timeline_clip_id)

        info = await client.effects.get_info(effect.id)
        if info.parameters:
            param = info.parameters[0]

            # Set keyframe at position 50
            result = await client.effects.set_keyframe(
                timeline_clip_id,
                effect.id,
                param.name,
                position=50,
                value=1.0,
            )
            assert result is True

            # Verify keyframe exists
            keyframes = await client.effects.get_keyframes(
                timeline_clip_id,
                effect.id,
                param.name,
            )
            assert any(k.position == 50 for k in keyframes)

    @pytest.mark.asyncio
    async def test_delete_keyframe(
        self,
        client_with_empty_project: KdenliveClient,
        sample_video_path: Path | None,
    ) -> None:
        """Test deleting a keyframe."""
        skip_without_sample_video(sample_video_path)
        client = client_with_empty_project

        # Setup clip with effect and keyframe
        clip_id = await client.bin.import_clip(str(sample_video_path))
        tracks = await client.timeline.get_tracks()
        video_track = next(t for t in tracks if t.type == "video")
        timeline_clip_id = await client.timeline.insert_clip(
            bin_clip_id=clip_id,
            track_id=video_track.id,
            position=0,
        )

        effects = await client.effects.list_available()
        effect = effects[0]
        await client.effects.add(effect.id, timeline_clip_id)

        info = await client.effects.get_info(effect.id)
        if info.parameters:
            param = info.parameters[0]

            # Add then delete keyframe
            await client.effects.set_keyframe(
                timeline_clip_id,
                effect.id,
                param.name,
                position=50,
                value=1.0,
            )

            result = await client.effects.delete_keyframe(
                timeline_clip_id,
                effect.id,
                param.name,
                position=50,
            )
            assert result is True
