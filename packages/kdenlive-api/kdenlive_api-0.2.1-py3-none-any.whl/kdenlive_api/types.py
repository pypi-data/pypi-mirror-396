"""Type definitions for Kdenlive API."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectInfo(BaseModel):
    """Project information."""

    model_config = ConfigDict(populate_by_name=True)

    path: str | None = None
    name: str | None = None
    profile: str | None = None
    fps: float = 0.0
    width: int = 0
    height: int = 0
    duration: int = 0  # frames
    modified: bool = False


class TrackInfo(BaseModel):
    """Track information."""

    id: int
    name: str
    type: Literal["video", "audio"]
    locked: bool = False
    muted: bool = False
    hidden: bool = False


class TimelineInfo(BaseModel):
    """Timeline information."""

    model_config = ConfigDict(populate_by_name=True)

    duration: int  # frames
    track_count: int = Field(default=0, validation_alias="trackCount")
    video_tracks: int = Field(default=0, validation_alias="videoTrackCount")
    audio_tracks: int = Field(default=0, validation_alias="audioTrackCount")
    position: int = 0


class ClipInfo(BaseModel):
    """Bin clip information."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    # Server may return int type code or string - accept any
    type: str | int = "unknown"
    duration: int = 0  # frames
    url: str = ""
    has_audio: bool = Field(default=True, alias="hasAudio")
    has_video: bool = Field(default=True, alias="hasVideo")
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    codec: str | None = None
    file_size: int | None = Field(default=None, alias="fileSize")
    folder_id: str | None = Field(default=None, alias="folderId")
    loading: bool = False  # True while async tasks (thumbnail/waveform) are in progress


class TimelineClip(BaseModel):
    """Timeline clip instance."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    bin_id: str = Field(alias="binId")
    track_id: int = Field(alias="trackId")
    position: int  # frames
    duration: int  # frames
    in_point: int = Field(alias="in")
    out_point: int = Field(alias="out")
    name: str | None = None


class FolderInfo(BaseModel):
    """Bin folder information."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    parent_id: str | None = Field(default=None, alias="parentId")


class Marker(BaseModel):
    """Clip or timeline marker."""

    id: int
    position: int  # frames
    comment: str = ""
    type: int = 0  # marker category
    color: str | None = None


class EffectInfo(BaseModel):
    """Effect information."""

    id: str
    name: str
    category: str = ""
    description: str = ""


class EffectDetailedInfo(BaseModel):
    """Detailed effect information with parameters."""

    id: str
    name: str
    category: str = ""
    description: str = ""
    parameters: list["EffectParameter"] = Field(default_factory=list)


class EffectParameter(BaseModel):
    """Effect parameter definition."""

    name: str
    type: str
    min: float | None = None
    max: float | None = None
    default: float | str | bool | None = None
    description: str = ""

    @field_validator("min", "max", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: Any) -> float | None:
        """Convert empty strings to None."""
        if v == "" or v is None:
            return None
        return float(v)


class ClipEffect(BaseModel):
    """Effect applied to a clip."""

    index: int
    id: str
    name: str
    enabled: bool = True


class Keyframe(BaseModel):
    """Effect keyframe."""

    position: int  # frames
    value: Any


class TransitionType(BaseModel):
    """Transition type information."""

    type: str
    name: str
    description: str = ""


class TransitionInfo(BaseModel):
    """Transition instance on timeline."""

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="transitionId")
    type: str
    from_clip_id: int = Field(alias="fromClipId")
    to_clip_id: int = Field(alias="toClipId")


class CompositionInfo(BaseModel):
    """Composition instance on timeline."""

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="compositionId")
    type: str
    track: int
    position: int
    duration: int


class AssetCategory(BaseModel):
    """Asset/effect category."""

    name: str
    count: int


class AssetSearchResult(BaseModel):
    """Asset search result."""

    id: str
    name: str
    type: Literal["effect", "transition", "composition"]


class FavoriteAsset(BaseModel):
    """Favorite asset."""

    id: str
    name: str
    type: Literal["effect", "transition", "composition"]


class EffectPreset(BaseModel):
    """Effect preset."""

    name: str
    description: str = ""


class RenderPreset(BaseModel):
    """Render preset information."""

    name: str
    extension: str
    group: str = ""
    description: str = ""


class RenderPresetDetail(BaseModel):
    """Detailed render preset information."""

    name: str
    extension: str
    group: str = ""
    description: str = ""
    params: dict[str, Any] | str = Field(default_factory=dict)  # Server may return string


class RenderJob(BaseModel):
    """Render job information."""

    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(alias="jobId")
    output_path: str = Field(alias="outputPath")
    status: Literal["idle", "pending", "running", "completed", "error"]
    progress: int = 0  # 0-100


class RenderStatus(BaseModel):
    """Detailed render status."""

    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(alias="jobId")
    status: Literal["idle", "pending", "running", "completed", "error"]
    progress: int = 0  # 0-100
    frame: int = 0
    total_frames: int = Field(default=0, alias="totalFrames")
    eta: int | None = None  # seconds
    error: str | None = None


class RenderProgress(BaseModel):
    """Render progress notification."""

    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(alias="jobId")
    progress: int  # 0-100
    frame: int


class GuideRenderJob(BaseModel):
    """Guide-based render job."""

    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(alias="jobId")
    output_path: str = Field(alias="outputPath")
