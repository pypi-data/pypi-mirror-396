"""Kdenlive API - Python client library for Kdenlive JSON-RPC API."""

from kdenlive_api.client import (
    DEFAULT_WS_URL,
    KDENLIVE_AUTH_TOKEN_ENV,
    KDENLIVE_WS_URL_ENV,
    KdenliveClient,
)
from kdenlive_api.exceptions import (
    ClipNotFoundError,
    ConnectionError,
    EffectNotFoundError,
    KdenliveError,
    ProjectNotOpenError,
    RenderInProgressError,
    TrackNotFoundError,
    ValidationError,
)
from kdenlive_api.types import (
    AssetCategory,
    AssetSearchResult,
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

__version__ = "0.1.0"
__all__ = [
    # Client
    "KdenliveClient",
    # Configuration
    "DEFAULT_WS_URL",
    "KDENLIVE_WS_URL_ENV",
    "KDENLIVE_AUTH_TOKEN_ENV",
    # Exceptions
    "KdenliveError",
    "ValidationError",
    "ConnectionError",
    "ProjectNotOpenError",
    "ClipNotFoundError",
    "TrackNotFoundError",
    "EffectNotFoundError",
    "RenderInProgressError",
    # Types - Project & Timeline
    "ProjectInfo",
    "TrackInfo",
    "TimelineInfo",
    "ClipInfo",
    "TimelineClip",
    "FolderInfo",
    "Marker",
    # Types - Effects
    "EffectInfo",
    "EffectDetailedInfo",
    "EffectParameter",
    "ClipEffect",
    "Keyframe",
    # Types - Transitions & Compositions
    "TransitionType",
    "TransitionInfo",
    "CompositionInfo",
    # Types - Assets
    "AssetCategory",
    "AssetSearchResult",
    "FavoriteAsset",
    "EffectPreset",
    # Types - Render
    "RenderPreset",
    "RenderPresetDetail",
    "RenderJob",
    "RenderStatus",
    "RenderProgress",
    "GuideRenderJob",
]
