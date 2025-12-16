"""Tests for type definitions."""

from __future__ import annotations

from kdenlive_api.types import (
    AssetCategory,
    ClipEffect,
    ClipInfo,
    CompositionInfo,
    EffectDetailedInfo,
    EffectInfo,
    EffectParameter,
    EffectPreset,
    FavoriteAsset,
    FolderInfo,
    GuideRenderJob,
    Keyframe,
    Marker,
    ProjectInfo,
    RenderJob,
    RenderPreset,
    RenderPresetDetail,
    RenderProgress,
    RenderStatus,
    TimelineClip,
    TimelineInfo,
    TrackInfo,
    TransitionInfo,
    TransitionType,
)


class TestProjectInfo:
    """Test ProjectInfo model."""

    def test_create_project_info(self) -> None:
        """Test creating ProjectInfo."""
        info = ProjectInfo(
            path="/test/project.kdenlive",
            name="Test Project",
            profile="atsc_1080p_25",
            fps=25.0,
            width=1920,
            height=1080,
            duration=7500,
            modified=False,
        )

        assert info.name == "Test Project"
        assert info.fps == 25.0

    def test_project_info_from_dict(self) -> None:
        """Test creating from dict with camelCase keys."""
        data = {
            "path": "/test.kdenlive",
            "name": "Test",
            "profile": "HD",
            "fps": 30.0,
            "width": 1920,
            "height": 1080,
            "duration": 1000,
            "modified": True,
        }
        info = ProjectInfo.model_validate(data)
        assert info.modified is True


class TestTimelineInfo:
    """Test TimelineInfo model."""

    def test_create_timeline_info(self) -> None:
        """Test creating TimelineInfo."""
        info = TimelineInfo(
            duration=7500,
            track_count=4,
            video_tracks=2,
            audio_tracks=2,
            position=0,
        )

        assert info.track_count == 4


class TestTrackInfo:
    """Test TrackInfo model."""

    def test_create_track_info(self) -> None:
        """Test creating TrackInfo."""
        track = TrackInfo(
            id=1,
            name="Video 1",
            type="video",
            locked=False,
            muted=False,
            hidden=False,
        )

        assert track.type == "video"
        assert track.locked is False


class TestClipInfo:
    """Test ClipInfo model."""

    def test_create_clip_info(self) -> None:
        """Test creating ClipInfo."""
        clip = ClipInfo(
            id="1",
            name="video.mp4",
            type="video",
            duration=5000,
            url="/path/to/video.mp4",
            has_audio=True,
            has_video=True,
            width=1920,
            height=1080,
        )

        assert clip.has_audio is True
        assert clip.width == 1920


class TestTimelineClip:
    """Test TimelineClip model."""

    def test_create_timeline_clip(self) -> None:
        """Test creating TimelineClip."""
        clip = TimelineClip(
            id=1,
            bin_id="clip1",
            track_id=1,
            position=0,
            duration=250,
            in_point=0,
            out_point=250,
            name="test.mp4",
        )

        assert clip.position == 0
        assert clip.duration == 250


class TestFolderInfo:
    """Test FolderInfo model."""

    def test_create_folder_info(self) -> None:
        """Test creating FolderInfo."""
        folder = FolderInfo(
            id="folder1",
            name="Raw Footage",
            parent_id=None,
        )

        assert folder.parent_id is None

    def test_folder_with_parent(self) -> None:
        """Test folder with parent."""
        folder = FolderInfo(
            id="folder2",
            name="B-Roll",
            parent_id="folder1",
        )

        assert folder.parent_id == "folder1"


class TestMarker:
    """Test Marker model."""

    def test_create_marker(self) -> None:
        """Test creating Marker."""
        marker = Marker(
            id=1,
            position=100,
            comment="Good take",
            type=0,
        )

        assert marker.comment == "Good take"


class TestEffectModels:
    """Test effect-related models."""

    def test_effect_info(self) -> None:
        """Test EffectInfo model."""
        effect = EffectInfo(
            id="brightness",
            name="Brightness",
            category="video",
            description="Adjust brightness",
        )

        assert effect.id == "brightness"

    def test_effect_parameter(self) -> None:
        """Test EffectParameter model."""
        param = EffectParameter(
            name="level",
            type="double",
            min=0.0,
            max=2.0,
            default=1.0,
        )

        assert param.default == 1.0

    def test_effect_detailed_info(self) -> None:
        """Test EffectDetailedInfo model."""
        info = EffectDetailedInfo(
            id="brightness",
            name="Brightness",
            category="video",
            description="Adjust brightness",
            parameters=[EffectParameter(name="level", type="double", min=0, max=2, default=1)],
        )

        assert len(info.parameters) == 1

    def test_clip_effect(self) -> None:
        """Test ClipEffect model."""
        effect = ClipEffect(
            index=0,
            id="brightness",
            name="Brightness",
            enabled=True,
        )

        assert effect.enabled is True

    def test_keyframe(self) -> None:
        """Test Keyframe model."""
        kf = Keyframe(
            position=50,
            value=1.5,
        )

        assert kf.value == 1.5


class TestTransitionModels:
    """Test transition models."""

    def test_transition_type(self) -> None:
        """Test TransitionType model."""
        t = TransitionType(
            type="dissolve",
            name="Dissolve",
            description="Cross dissolve",
        )

        assert t.type == "dissolve"

    def test_transition_info(self) -> None:
        """Test TransitionInfo model."""
        t = TransitionInfo(
            id=1,
            type="dissolve",
            from_clip_id=5,
            to_clip_id=6,
        )

        assert t.type == "dissolve"


class TestCompositionInfo:
    """Test CompositionInfo model."""

    def test_create_composition(self) -> None:
        """Test creating CompositionInfo."""
        comp = CompositionInfo(
            id=1,
            type="qtblend",
            track=2,
            position=0,
            duration=250,
        )

        assert comp.type == "qtblend"


class TestAssetModels:
    """Test asset models."""

    def test_asset_category(self) -> None:
        """Test AssetCategory model."""
        cat = AssetCategory(
            name="Video Effects",
            count=45,
        )

        assert cat.count == 45

    def test_favorite_asset(self) -> None:
        """Test FavoriteAsset model."""
        fav = FavoriteAsset(
            id="brightness",
            name="Brightness",
            type="effect",
        )

        assert fav.type == "effect"

    def test_effect_preset(self) -> None:
        """Test EffectPreset model."""
        preset = EffectPreset(
            name="Bright",
            description="Bright preset",
        )

        assert preset.name == "Bright"


class TestRenderModels:
    """Test render models."""

    def test_render_preset(self) -> None:
        """Test RenderPreset model."""
        preset = RenderPreset(
            name="YouTube 1080p",
            extension="mp4",
        )

        assert preset.extension == "mp4"

    def test_render_preset_detail(self) -> None:
        """Test RenderPresetDetail model."""
        detail = RenderPresetDetail(
            name="YouTube 1080p",
            extension="mp4",
            params={"crf": "18"},
        )

        assert detail.params["crf"] == "18"

    def test_render_job(self) -> None:
        """Test RenderJob model."""
        job = RenderJob(
            job_id="job_123",
            output_path="/output/video.mp4",
            status="pending",
            progress=0,
        )

        assert job.status == "pending"

    def test_render_status(self) -> None:
        """Test RenderStatus model."""
        status = RenderStatus(
            job_id="job_123",
            status="running",
            progress=45,
            frame=3375,
            total_frames=7500,
            eta=120,
        )

        assert status.eta == 120

    def test_render_progress(self) -> None:
        """Test RenderProgress model."""
        progress = RenderProgress(
            job_id="job_123",
            progress=50,
            frame=3750,
        )

        assert progress.progress == 50

    def test_guide_render_job(self) -> None:
        """Test GuideRenderJob model."""
        job = GuideRenderJob(
            job_id="job_124",
            output_path="/output/Scene 1.mp4",
        )

        assert job.output_path == "/output/Scene 1.mp4"
