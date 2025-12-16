"""Tests for input validation models."""

import pytest
from kdenlive_api.validators import (
    BinCreateFolderInput,
    BinImportClipInput,
    BinImportClipsInput,
    EffectAddInput,
    ProjectOpenInput,
    ProjectSaveInput,
    RenderStartInput,
    TimelineAddTrackInput,
    TimelineInsertClipInput,
    TimelineMoveClipInput,
    TimelineResizeClipInput,
    TimelineSeekInput,
    TransitionAddInput,
)
from pydantic import ValidationError


class TestProjectValidators:
    """Tests for project input validators."""

    def test_project_open_valid(self):
        """Test valid project open input."""
        result = ProjectOpenInput(path="/home/user/project.kdenlive")
        assert result.path == "/home/user/project.kdenlive"

    def test_project_open_invalid_extension(self):
        """Test project open rejects non-kdenlive files."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectOpenInput(path="/home/user/project.xml")
        assert "kdenlive extension" in str(exc_info.value).lower()

    def test_project_open_empty_path(self):
        """Test project open rejects empty path."""
        with pytest.raises(ValidationError):
            ProjectOpenInput(path="")

    def test_project_open_whitespace_stripped(self):
        """Test whitespace is stripped from path."""
        result = ProjectOpenInput(path="  /home/user/project.kdenlive  ")
        assert result.path == "/home/user/project.kdenlive"

    def test_project_save_optional_path(self):
        """Test project save allows None path."""
        result = ProjectSaveInput(path=None)
        assert result.path is None

    def test_project_save_valid_path(self):
        """Test project save with valid path."""
        result = ProjectSaveInput(path="/home/user/new.kdenlive")
        assert result.path == "/home/user/new.kdenlive"

    def test_project_save_invalid_extension(self):
        """Test project save rejects invalid extension."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectSaveInput(path="/home/user/project.mp4")
        assert "kdenlive extension" in str(exc_info.value).lower()


class TestTimelineValidators:
    """Tests for timeline input validators."""

    def test_timeline_insert_clip_valid(self):
        """Test valid insert clip input."""
        result = TimelineInsertClipInput(bin_clip_id="clip1", track_id=0, position=100)
        assert result.bin_clip_id == "clip1"
        assert result.track_id == 0
        assert result.position == 100

    def test_timeline_insert_clip_empty_bin_id(self):
        """Test insert clip rejects empty bin clip ID."""
        with pytest.raises(ValidationError):
            TimelineInsertClipInput(bin_clip_id="", track_id=0, position=0)

    def test_timeline_insert_clip_negative_track(self):
        """Test insert clip rejects negative track ID."""
        with pytest.raises(ValidationError):
            TimelineInsertClipInput(bin_clip_id="clip1", track_id=-1, position=0)

    def test_timeline_insert_clip_negative_position(self):
        """Test insert clip rejects negative position."""
        with pytest.raises(ValidationError):
            TimelineInsertClipInput(bin_clip_id="clip1", track_id=0, position=-100)

    def test_timeline_insert_clip_in_out_valid(self):
        """Test insert clip with valid in/out points."""
        result = TimelineInsertClipInput(
            bin_clip_id="clip1", track_id=0, position=0, in_point=10, out_point=100
        )
        assert result.in_point == 10
        assert result.out_point == 100

    def test_timeline_insert_clip_in_out_invalid(self):
        """Test insert clip rejects in >= out."""
        with pytest.raises(ValidationError) as exc_info:
            TimelineInsertClipInput(
                bin_clip_id="clip1", track_id=0, position=0, in_point=100, out_point=50
            )
        assert "in_point must be less than out_point" in str(exc_info.value)

    def test_timeline_insert_clip_in_equals_out(self):
        """Test insert clip rejects in == out."""
        with pytest.raises(ValidationError):
            TimelineInsertClipInput(
                bin_clip_id="clip1", track_id=0, position=0, in_point=50, out_point=50
            )

    def test_timeline_move_clip_valid(self):
        """Test valid move clip input."""
        result = TimelineMoveClipInput(clip_id=5, track_id=1, position=200)
        assert result.clip_id == 5
        assert result.track_id == 1
        assert result.position == 200

    def test_timeline_resize_clip_valid(self):
        """Test valid resize clip input."""
        result = TimelineResizeClipInput(clip_id=5, in_point=10, out_point=100)
        assert result.clip_id == 5
        assert result.in_point == 10
        assert result.out_point == 100

    def test_timeline_resize_clip_invalid_points(self):
        """Test resize clip rejects invalid in/out points."""
        with pytest.raises(ValidationError):
            TimelineResizeClipInput(clip_id=5, in_point=100, out_point=50)

    def test_timeline_add_track_video(self):
        """Test add video track."""
        result = TimelineAddTrackInput(track_type="video")
        assert result.track_type == "video"

    def test_timeline_add_track_audio(self):
        """Test add audio track."""
        result = TimelineAddTrackInput(track_type="audio")
        assert result.track_type == "audio"

    def test_timeline_add_track_invalid_type(self):
        """Test add track rejects invalid type."""
        with pytest.raises(ValidationError):
            TimelineAddTrackInput(track_type="subtitle")  # type: ignore[arg-type]

    def test_timeline_add_track_with_name(self):
        """Test add track with name."""
        result = TimelineAddTrackInput(track_type="video", name="Main Video")
        assert result.name == "Main Video"

    def test_timeline_add_track_empty_name_becomes_none(self):
        """Test add track with empty name becomes None."""
        result = TimelineAddTrackInput(track_type="video", name="   ")
        assert result.name is None

    def test_timeline_seek_valid(self):
        """Test valid seek position."""
        result = TimelineSeekInput(position=1500)
        assert result.position == 1500

    def test_timeline_seek_zero(self):
        """Test seek to position 0 is valid."""
        result = TimelineSeekInput(position=0)
        assert result.position == 0

    def test_timeline_seek_negative(self):
        """Test seek rejects negative position."""
        with pytest.raises(ValidationError):
            TimelineSeekInput(position=-100)


class TestBinValidators:
    """Tests for bin input validators."""

    def test_bin_import_clip_valid_path(self):
        """Test valid absolute path."""
        result = BinImportClipInput(url="/home/user/video.mp4")
        assert result.url == "/home/user/video.mp4"

    def test_bin_import_clip_valid_http(self):
        """Test valid HTTP URL."""
        result = BinImportClipInput(url="http://example.com/video.mp4")
        assert result.url == "http://example.com/video.mp4"

    def test_bin_import_clip_valid_https(self):
        """Test valid HTTPS URL."""
        result = BinImportClipInput(url="https://example.com/video.mp4")
        assert result.url == "https://example.com/video.mp4"

    def test_bin_import_clip_invalid_relative(self):
        """Test import clip rejects relative path."""
        with pytest.raises(ValidationError):
            BinImportClipInput(url="videos/clip.mp4")

    def test_bin_import_clip_empty(self):
        """Test import clip rejects empty URL."""
        with pytest.raises(ValidationError):
            BinImportClipInput(url="")

    def test_bin_import_clips_valid(self):
        """Test valid import clips input."""
        result = BinImportClipsInput(urls=["/path/to/video1.mp4", "/path/to/video2.mp4"])
        assert len(result.urls) == 2

    def test_bin_import_clips_empty_list(self):
        """Test import clips rejects empty list."""
        with pytest.raises(ValidationError):
            BinImportClipsInput(urls=[])

    def test_bin_import_clips_invalid_url_in_list(self):
        """Test import clips rejects invalid URL in list."""
        with pytest.raises(ValidationError):
            BinImportClipsInput(urls=["/valid/path.mp4", "relative/path.mp4"])

    def test_bin_create_folder_valid(self):
        """Test valid folder creation."""
        result = BinCreateFolderInput(name="Raw Footage")
        assert result.name == "Raw Footage"

    def test_bin_create_folder_empty_name(self):
        """Test create folder rejects empty name."""
        with pytest.raises(ValidationError):
            BinCreateFolderInput(name="")


class TestEffectValidators:
    """Tests for effect input validators."""

    def test_effect_add_valid(self):
        """Test valid effect add input."""
        result = EffectAddInput(effect_id="brightness", clip_id=5)
        assert result.effect_id == "brightness"
        assert result.clip_id == 5

    def test_effect_add_empty_effect_id(self):
        """Test effect add rejects empty effect ID."""
        with pytest.raises(ValidationError):
            EffectAddInput(effect_id="", clip_id=5)

    def test_effect_add_negative_clip_id(self):
        """Test effect add rejects negative clip ID."""
        with pytest.raises(ValidationError):
            EffectAddInput(effect_id="brightness", clip_id=-1)


class TestRenderValidators:
    """Tests for render input validators."""

    def test_render_start_valid(self):
        """Test valid render start input."""
        result = RenderStartInput(preset_name="YouTube 1080p", output_path="/home/user/output.mp4")
        assert result.preset_name == "YouTube 1080p"
        assert result.output_path == "/home/user/output.mp4"

    def test_render_start_empty_preset(self):
        """Test render start rejects empty preset."""
        with pytest.raises(ValidationError):
            RenderStartInput(preset_name="", output_path="/home/user/output.mp4")

    def test_render_start_relative_path(self):
        """Test render start rejects relative output path."""
        with pytest.raises(ValidationError):
            RenderStartInput(preset_name="YouTube 1080p", output_path="output.mp4")

    def test_render_start_with_in_out(self):
        """Test render start with in/out points."""
        result = RenderStartInput(
            preset_name="YouTube 1080p",
            output_path="/home/user/output.mp4",
            in_point=0,
            out_point=1000,
        )
        assert result.in_point == 0
        assert result.out_point == 1000

    def test_render_start_invalid_in_out(self):
        """Test render start rejects invalid in/out points."""
        with pytest.raises(ValidationError):
            RenderStartInput(
                preset_name="YouTube 1080p",
                output_path="/home/user/output.mp4",
                in_point=1000,
                out_point=500,
            )


class TestTransitionValidators:
    """Tests for transition input validators."""

    def test_transition_add_valid(self):
        """Test valid transition add input."""
        result = TransitionAddInput(transition_type="dissolve", from_clip_id=1, to_clip_id=2)
        assert result.transition_type == "dissolve"
        assert result.from_clip_id == 1
        assert result.to_clip_id == 2

    def test_transition_add_same_clips(self):
        """Test transition add rejects same clip IDs."""
        with pytest.raises(ValidationError) as exc_info:
            TransitionAddInput(transition_type="dissolve", from_clip_id=5, to_clip_id=5)
        assert "must be different" in str(exc_info.value)

    def test_transition_add_empty_type(self):
        """Test transition add rejects empty type."""
        with pytest.raises(ValidationError):
            TransitionAddInput(transition_type="", from_clip_id=1, to_clip_id=2)

    def test_transition_add_negative_clip_ids(self):
        """Test transition add rejects negative clip IDs."""
        with pytest.raises(ValidationError):
            TransitionAddInput(transition_type="dissolve", from_clip_id=-1, to_clip_id=2)

    def test_transition_add_with_duration(self):
        """Test transition add with duration."""
        result = TransitionAddInput(
            transition_type="dissolve", from_clip_id=1, to_clip_id=2, duration=25
        )
        assert result.duration == 25

    def test_transition_add_zero_duration(self):
        """Test transition add rejects zero duration."""
        with pytest.raises(ValidationError):
            TransitionAddInput(transition_type="dissolve", from_clip_id=1, to_clip_id=2, duration=0)
