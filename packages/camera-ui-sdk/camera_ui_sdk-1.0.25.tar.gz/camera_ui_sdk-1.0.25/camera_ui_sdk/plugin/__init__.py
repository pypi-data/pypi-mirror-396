"""Plugin module exports."""

from .interfaces import (
    AudioFrameData,
    AudioResult,
    ClassifierResult,
    FaceResult,
    LicensePlateResult,
    MotionResult,
    ObjectResult,
    VideoFrameData,
)
from .types import (
    APIEventType,
    APIListener,
    AudioDetectionPluginResponse,
    AudioMetadata,
    CuiPlugin,
    ImageMetadata,
    MotionDetectionPluginResponse,
    ObjectDetectionPluginResponse,
    PluginAPI,
    PluginContract,
    PluginInfo,
    PluginRole,
)

__all__ = [
    # Event types
    "APIEventType",
    "APIListener",
    # Interfaces (detection results)
    "AudioFrameData",
    "AudioResult",
    "ClassifierResult",
    "FaceResult",
    "LicensePlateResult",
    "MotionResult",
    "ObjectResult",
    "VideoFrameData",
    # Types
    "ImageMetadata",
    "AudioMetadata",
    "MotionDetectionPluginResponse",
    "ObjectDetectionPluginResponse",
    "AudioDetectionPluginResponse",
    "PluginAPI",
    "CuiPlugin",
    "PluginContract",
    "PluginInfo",
    "PluginRole",
]
