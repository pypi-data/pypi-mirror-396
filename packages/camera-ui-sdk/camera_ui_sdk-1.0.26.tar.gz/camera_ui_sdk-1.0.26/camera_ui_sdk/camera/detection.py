"""Detection zone and settings types."""

from __future__ import annotations

from typing import Literal, TypedDict

from .types import MotionResolution, Point, ZoneFilter, ZoneType

# Base detection labels - always available for zone filtering.
# These are the built-in categories that the system understands.
BaseDetectionLabel = Literal[
    "motion",
    "person",
    "vehicle",
    "animal",
    "package",
    "face",
    "license_plate",
    "audio",
]

# Base detection labels as tuple - for iteration and validation
BASE_DETECTION_LABELS: tuple[BaseDetectionLabel, ...] = (
    "motion",
    "person",
    "vehicle",
    "animal",
    "package",
    "face",
    "license_plate",
    "audio",
)

# Detection label type - base category or any plugin-provided label
# In Python, we use str since Python doesn't have the TypeScript (string & {}) trick
DetectionLabel = str


class PluginLabels(TypedDict):
    """Plugin-provided labels from a sensor's modelSpec."""

    sensorId: str
    sensorName: str
    pluginId: str
    labels: list[str]


class AvailableLabels(TypedDict):
    """Available detection labels for a camera."""

    base: tuple[BaseDetectionLabel, ...]
    plugins: list[PluginLabels]
    all: list[str]


class DetectionZone(TypedDict):
    """Detection zone configuration."""

    name: str
    points: list[Point]
    type: ZoneType
    filter: ZoneFilter
    labels: list[DetectionLabel]
    isPrivacyMask: bool
    color: str


class MotionDetectionSettings(TypedDict):
    """Motion detection settings."""

    timeout: int
    resolution: MotionResolution


class ObjectDetectionSettings(TypedDict):
    """Object detection settings."""

    confidence: float
    timeout: int


class CameraDetectionSettings(TypedDict):
    """Camera detection settings."""

    motion: MotionDetectionSettings
    object: ObjectDetectionSettings
