"""Input validation models for Kdenlive API.

These models validate parameters BEFORE sending to the WebSocket server,
catching type errors and semantic usage errors early.
"""

from __future__ import annotations

import os
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# =============================================================================
# Base Configuration
# =============================================================================


class InputModel(BaseModel):
    """Base model for input validation with strict settings."""

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Strip whitespace from strings
        validate_assignment=True,  # Validate on attribute assignment
        extra="forbid",  # Reject unknown fields
    )


# =============================================================================
# Common Types
# =============================================================================

TrackType = Literal["video", "audio"]
ClipType = Literal["video", "audio", "image", "color", "text"]
AssetType = Literal["effect", "transition", "composition"]
RenderStatus = Literal["pending", "running", "completed", "error"]
TrackProperty = Literal["name", "locked", "muted", "hidden"]

# Annotated types for reusable constraints
PositiveInt = Annotated[int, Field(ge=0, description="Non-negative integer (frames/position)")]
PositiveFloat = Annotated[float, Field(gt=0, description="Positive float")]
NonEmptyStr = Annotated[str, Field(min_length=1, description="Non-empty string")]
ClipIdStr = Annotated[str, Field(min_length=1, description="Bin clip ID")]
EffectIdStr = Annotated[str, Field(min_length=1, description="Effect ID")]


# =============================================================================
# Project Validators
# =============================================================================


class ProjectOpenInput(InputModel):
    """Validate project.open parameters."""

    path: NonEmptyStr = Field(description="Path to .kdenlive project file")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate project path has correct extension."""
        if not v.endswith(".kdenlive"):
            raise ValueError("Project path must have .kdenlive extension")
        return v


class ProjectSaveInput(InputModel):
    """Validate project.save parameters."""

    path: str | None = Field(default=None, description="Optional new path to save to")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str | None) -> str | None:
        """Validate path if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not v.endswith(".kdenlive"):
                raise ValueError("Project path must have .kdenlive extension")
        return v


class ProjectNewInput(InputModel):
    """Validate project.new parameters."""

    profile: str | None = Field(default=None, description="Video profile")


# =============================================================================
# Timeline Validators
# =============================================================================


class TimelineInsertClipInput(InputModel):
    """Validate timeline.insertClip parameters."""

    bin_clip_id: ClipIdStr = Field(description="ID of clip in bin")
    track_id: int = Field(ge=0, description="Target track ID")
    position: PositiveInt = Field(description="Position in frames")
    in_point: PositiveInt | None = Field(default=None, description="Optional in point")
    out_point: PositiveInt | None = Field(default=None, description="Optional out point")

    @model_validator(mode="after")
    def validate_in_out_points(self) -> TimelineInsertClipInput:
        """Validate in/out point relationship."""
        if (
            self.in_point is not None
            and self.out_point is not None
            and self.in_point >= self.out_point
        ):
            raise ValueError("in_point must be less than out_point")
        return self


class TimelineMoveClipInput(InputModel):
    """Validate timeline.moveClip parameters."""

    clip_id: int = Field(ge=0, description="Clip ID to move")
    track_id: int = Field(ge=0, description="Target track ID")
    position: PositiveInt = Field(description="New position in frames")


class TimelineDeleteClipInput(InputModel):
    """Validate timeline.deleteClip parameters."""

    clip_id: int = Field(ge=0, description="Clip ID to delete")


class TimelineDeleteClipsInput(InputModel):
    """Validate timeline.deleteClips parameters."""

    clip_ids: list[int] = Field(min_length=1, description="List of clip IDs to delete")

    @field_validator("clip_ids")
    @classmethod
    def validate_clip_ids(cls, v: list[int]) -> list[int]:
        """Validate all clip IDs are non-negative."""
        for clip_id in v:
            if clip_id < 0:
                raise ValueError(f"Invalid clip ID: {clip_id} (must be non-negative)")
        return v


class TimelineResizeClipInput(InputModel):
    """Validate timeline.resizeClip parameters."""

    clip_id: int = Field(ge=0, description="Clip ID to resize")
    in_point: PositiveInt = Field(description="New in point")
    out_point: PositiveInt = Field(description="New out point")

    @model_validator(mode="after")
    def validate_in_out(self) -> TimelineResizeClipInput:
        """Validate in < out."""
        if self.in_point >= self.out_point:
            raise ValueError("in_point must be less than out_point")
        return self


class TimelineSplitClipInput(InputModel):
    """Validate timeline.splitClip parameters."""

    clip_id: int = Field(ge=0, description="Clip ID to split")
    position: PositiveInt = Field(description="Split position in frames")


class TimelineAddTrackInput(InputModel):
    """Validate timeline.addTrack parameters."""

    track_type: TrackType = Field(description="Track type: 'video' or 'audio'")
    name: str | None = Field(default=None, description="Optional track name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate name if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class TimelineDeleteTrackInput(InputModel):
    """Validate timeline.deleteTrack parameters."""

    track_id: int = Field(ge=0, description="Track ID to delete")


class TimelineSeekInput(InputModel):
    """Validate timeline.seek parameters."""

    position: PositiveInt = Field(description="Target position in frames")


class TimelineGetClipsInput(InputModel):
    """Validate timeline.getClips parameters."""

    track_id: int | None = Field(default=None, ge=0, description="Optional track filter")


class TimelineSetSelectionInput(InputModel):
    """Validate timeline.setSelection parameters."""

    clip_ids: list[int] = Field(description="Clip IDs to select")

    @field_validator("clip_ids")
    @classmethod
    def validate_clip_ids(cls, v: list[int]) -> list[int]:
        """Validate all clip IDs are non-negative."""
        for clip_id in v:
            if clip_id < 0:
                raise ValueError(f"Invalid clip ID: {clip_id}")
        return v


class TimelineSetTrackPropertyInput(InputModel):
    """Validate timeline.setTrackProperty parameters."""

    track_id: int = Field(ge=0, description="Track ID")
    property_name: TrackProperty = Field(description="Property name")
    value: str | bool = Field(description="Property value")


# =============================================================================
# Bin Validators
# =============================================================================


class BinImportClipInput(InputModel):
    """Validate bin.importClip parameters."""

    url: NonEmptyStr = Field(description="Path to media file")
    folder_id: str | None = Field(default=None, description="Target folder ID")
    server_timeout: int | None = Field(
        default=None,
        ge=0,
        description="Server timeout in ms (0=immediate return, None=default 10s)",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate media URL/path."""
        # Allow URLs and file paths
        if not (v.startswith(("http://", "https://", "file://", "/")) or os.path.isabs(v)):
            raise ValueError("URL must be an absolute path or valid URL")
        return v


class BinImportClipsInput(InputModel):
    """Validate bin.importClips parameters."""

    urls: list[str] = Field(min_length=1, description="List of media file paths")
    folder_id: str | None = Field(default=None, description="Target folder ID")
    server_timeout: int | None = Field(
        default=None,
        ge=0,
        description="Server timeout in ms per clip (0=immediate return, None=default 10s)",
    )

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: list[str]) -> list[str]:
        """Validate all URLs."""
        for url in v:
            url = url.strip()
            if not url:
                raise ValueError("Empty URL in list")
            if not (url.startswith(("http://", "https://", "file://", "/")) or os.path.isabs(url)):
                raise ValueError(f"Invalid URL: {url}")
        return v


class BinDeleteClipInput(InputModel):
    """Validate bin.deleteClip parameters."""

    clip_id: ClipIdStr = Field(description="Clip ID to delete")


class BinDeleteClipsInput(InputModel):
    """Validate bin.deleteClips parameters."""

    clip_ids: list[str] = Field(min_length=1, description="List of clip IDs")

    @field_validator("clip_ids")
    @classmethod
    def validate_clip_ids(cls, v: list[str]) -> list[str]:
        """Validate clip IDs are non-empty."""
        for clip_id in v:
            if not clip_id.strip():
                raise ValueError("Empty clip ID in list")
        return [c.strip() for c in v]


class BinGetClipInfoInput(InputModel):
    """Validate bin.getClipInfo parameters."""

    clip_id: ClipIdStr = Field(description="Clip ID")


class BinCreateFolderInput(InputModel):
    """Validate bin.createFolder parameters."""

    name: NonEmptyStr = Field(description="Folder name")
    parent_id: str | None = Field(default=None, description="Parent folder ID")


class BinDeleteFolderInput(InputModel):
    """Validate bin.deleteFolder parameters."""

    folder_id: NonEmptyStr = Field(description="Folder ID to delete")


class BinRenameItemInput(InputModel):
    """Validate bin.renameItem parameters."""

    item_id: NonEmptyStr = Field(description="Item ID to rename")
    name: NonEmptyStr = Field(description="New name")


class BinMoveItemInput(InputModel):
    """Validate bin.moveItem parameters."""

    item_id: NonEmptyStr = Field(description="Item ID to move")
    target_folder_id: NonEmptyStr = Field(description="Target folder ID")


class BinListClipsInput(InputModel):
    """Validate bin.listClips parameters."""

    folder_id: str | None = Field(default=None, description="Folder filter")


class BinAddClipMarkerInput(InputModel):
    """Validate bin.addClipMarker parameters."""

    clip_id: ClipIdStr = Field(description="Clip ID")
    position: PositiveInt = Field(description="Marker position in frames")
    comment: str = Field(default="", description="Marker comment")


class BinDeleteClipMarkerInput(InputModel):
    """Validate bin.deleteClipMarker parameters."""

    clip_id: ClipIdStr = Field(description="Clip ID")
    marker_id: int = Field(ge=0, description="Marker ID")


class BinGetClipMarkersInput(InputModel):
    """Validate bin.getClipMarkers parameters."""

    clip_id: ClipIdStr = Field(description="Clip ID")


# =============================================================================
# Effect Validators
# =============================================================================


class EffectGetInfoInput(InputModel):
    """Validate effect.getInfo parameters."""

    effect_id: EffectIdStr = Field(description="Effect ID")


class EffectAddInput(InputModel):
    """Validate effect.add parameters."""

    effect_id: EffectIdStr = Field(description="Effect ID to add")
    clip_id: int = Field(ge=0, description="Target clip ID")


class EffectRemoveInput(InputModel):
    """Validate effect.remove parameters."""

    clip_id: int = Field(ge=0, description="Clip ID")
    effect_id: EffectIdStr = Field(description="Effect instance ID")


class EffectGetClipEffectsInput(InputModel):
    """Validate effect.getClipEffects parameters."""

    clip_id: int = Field(ge=0, description="Clip ID")


class EffectSetPropertyInput(InputModel):
    """Validate effect.setProperty parameters."""

    clip_id: int = Field(ge=0, description="Clip ID")
    effect_id: EffectIdStr = Field(description="Effect instance ID")
    property_name: NonEmptyStr = Field(description="Property name")
    value: Any = Field(description="Property value")


class EffectGetPropertyInput(InputModel):
    """Validate effect.getProperty parameters."""

    clip_id: int = Field(ge=0, description="Clip ID")
    effect_id: EffectIdStr = Field(description="Effect instance ID")
    property_name: NonEmptyStr = Field(description="Property name")


class EffectEnableDisableInput(InputModel):
    """Validate effect.enable/disable parameters."""

    clip_id: int = Field(ge=0, description="Clip ID")
    effect_id: EffectIdStr = Field(description="Effect instance ID")


class EffectReorderInput(InputModel):
    """Validate effect.reorder parameters."""

    clip_id: int = Field(ge=0, description="Clip ID")
    effect_id: EffectIdStr = Field(description="Effect ID")
    new_index: int = Field(ge=0, description="New index position")


class EffectCopyToClipsInput(InputModel):
    """Validate effect.copyToClips parameters."""

    source_clip_id: int = Field(ge=0, description="Source clip ID")
    effect_id: EffectIdStr = Field(description="Effect ID to copy")
    target_clip_ids: list[int] = Field(min_length=1, description="Target clip IDs")

    @field_validator("target_clip_ids")
    @classmethod
    def validate_target_ids(cls, v: list[int]) -> list[int]:
        """Validate target clip IDs."""
        for clip_id in v:
            if clip_id < 0:
                raise ValueError(f"Invalid target clip ID: {clip_id}")
        return v


class EffectKeyframeInput(InputModel):
    """Validate effect keyframe operations."""

    clip_id: int = Field(ge=0, description="Clip ID")
    effect_id: EffectIdStr = Field(description="Effect ID")
    property_name: NonEmptyStr = Field(description="Property name")
    position: PositiveInt = Field(description="Keyframe position")


class EffectSetKeyframeInput(EffectKeyframeInput):
    """Validate effect.setKeyframe parameters."""

    value: Any = Field(description="Keyframe value")


# =============================================================================
# Render Validators
# =============================================================================


class RenderStartInput(InputModel):
    """Validate render.start parameters."""

    preset_name: NonEmptyStr = Field(description="Render preset name")
    output_path: NonEmptyStr = Field(description="Output file path")
    in_point: PositiveInt | None = Field(default=None, description="Start frame")
    out_point: PositiveInt | None = Field(default=None, description="End frame")

    @model_validator(mode="after")
    def validate_in_out(self) -> RenderStartInput:
        """Validate in/out points."""
        if (
            self.in_point is not None
            and self.out_point is not None
            and self.in_point >= self.out_point
        ):
            raise ValueError("in_point must be less than out_point")
        return self

    @field_validator("output_path")
    @classmethod
    def validate_output_path(cls, v: str) -> str:
        """Validate output path."""
        if not os.path.isabs(v):
            raise ValueError("Output path must be absolute")
        return v


class RenderStopInput(InputModel):
    """Validate render.stop parameters."""

    job_id: NonEmptyStr = Field(description="Job ID to stop")


class RenderGetStatusInput(InputModel):
    """Validate render.getStatus parameters."""

    job_id: NonEmptyStr = Field(description="Job ID")


class RenderGetPresetInfoInput(InputModel):
    """Validate render.getPresetInfo parameters."""

    preset_name: NonEmptyStr = Field(description="Preset name")


class RenderStartWithGuidesInput(InputModel):
    """Validate render.startWithGuides parameters."""

    preset_name: NonEmptyStr = Field(description="Render preset name")
    output_dir: NonEmptyStr = Field(description="Output directory")

    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v: str) -> str:
        """Validate output directory."""
        if not os.path.isabs(v):
            raise ValueError("Output directory must be absolute path")
        return v


# =============================================================================
# Transition Validators
# =============================================================================


class TransitionAddInput(InputModel):
    """Validate transition.add parameters."""

    transition_type: NonEmptyStr = Field(description="Transition type")
    from_clip_id: int = Field(ge=0, description="First clip ID")
    to_clip_id: int = Field(ge=0, description="Second clip ID")
    duration: int | None = Field(default=None, ge=1, description="Duration in frames")

    @model_validator(mode="after")
    def validate_different_clips(self) -> TransitionAddInput:
        """Ensure clips are different."""
        if self.from_clip_id == self.to_clip_id:
            raise ValueError("from_clip_id and to_clip_id must be different")
        return self


class TransitionRemoveInput(InputModel):
    """Validate transition.remove parameters."""

    transition_id: int = Field(ge=0, description="Transition ID")


class TransitionSetPropertyInput(InputModel):
    """Validate transition.setProperty parameters."""

    transition_id: int = Field(ge=0, description="Transition ID")
    property_name: NonEmptyStr = Field(description="Property name")
    value: Any = Field(description="Property value")


# =============================================================================
# Composition Validators
# =============================================================================


class CompositionAddInput(InputModel):
    """Validate composition.add parameters."""

    composition_type: NonEmptyStr = Field(description="Composition type")
    track: int = Field(ge=0, description="Track number")
    position: PositiveInt = Field(description="Position in frames")
    duration: int | None = Field(default=None, ge=1, description="Duration in frames")


class CompositionRemoveInput(InputModel):
    """Validate composition.remove parameters."""

    composition_id: int = Field(ge=0, description="Composition ID")


class CompositionSetPropertyInput(InputModel):
    """Validate composition.setProperty parameters."""

    composition_id: int = Field(ge=0, description="Composition ID")
    property_name: NonEmptyStr = Field(description="Property name")
    value: Any = Field(description="Property value")


# =============================================================================
# Asset Validators
# =============================================================================


class AssetSearchInput(InputModel):
    """Validate asset.search parameters."""

    query: NonEmptyStr = Field(description="Search query")


class AssetGetEffectsByCategoryInput(InputModel):
    """Validate asset.getEffectsByCategory parameters."""

    category: NonEmptyStr = Field(description="Category name")


class AssetFavoriteInput(InputModel):
    """Validate asset favorite operations."""

    asset_id: NonEmptyStr = Field(description="Asset ID")


class AssetGetPresetsInput(InputModel):
    """Validate asset.getPresets parameters."""

    effect_id: EffectIdStr = Field(description="Effect ID")


class AssetSavePresetInput(InputModel):
    """Validate asset.savePreset parameters."""

    effect_id: EffectIdStr = Field(description="Effect ID")
    preset_name: NonEmptyStr = Field(description="Preset name")


class AssetDeletePresetInput(InputModel):
    """Validate asset.deletePreset parameters."""

    effect_id: EffectIdStr = Field(description="Effect ID")
    preset_name: NonEmptyStr = Field(description="Preset name")


# =============================================================================
# RPC Validators
# =============================================================================


class RpcSubscribeInput(InputModel):
    """Validate rpc.subscribe parameters."""

    events: list[str] = Field(min_length=1, description="Events to subscribe to")

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: list[str]) -> list[str]:
        """Validate event names."""
        valid_events = {
            "render.progress",
            "render.finished",
            "project.modified",
            "timeline.changed",
        }
        for event in v:
            if event not in valid_events:
                raise ValueError(f"Unknown event: {event}. Valid: {valid_events}")
        return v


# =============================================================================
# Validation Helper
# =============================================================================


def validate_input(model_class: type[InputModel], **kwargs) -> dict[str, Any]:
    """Validate input and return cleaned parameters.

    Args:
        model_class: The Pydantic model class for validation
        **kwargs: Input parameters to validate

    Returns:
        Validated and cleaned parameters as a dict

    Raises:
        ValueError: If validation fails with descriptive message
    """
    try:
        validated = model_class.model_validate(kwargs)
        return validated.model_dump(exclude_none=True)
    except Exception as e:
        # Re-raise with cleaner message
        raise ValueError(f"Invalid input: {e}") from e
