"""Face sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import Detection, FaceDetection, ModelSpec, SensorCategory, SensorType

if TYPE_CHECKING:
    from ..plugin.interfaces import FaceResult, VideoFrameData


class FaceProperty(str, Enum):
    """Face sensor properties."""

    Detected = "detected"
    Faces = "faces"


class FaceSensorProperties(TypedDict):
    """Face sensor properties interface."""

    detected: bool
    faces: list[FaceDetection]


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class FaceSensorLike(SensorLike, Protocol):
    """Protocol for face sensor type checking."""

    @property
    def detected(self) -> bool:
        """Whether faces are currently detected."""
        ...

    @property
    def faces(self) -> list[FaceDetection]:
        """Current face detections."""
        ...


@runtime_checkable
class FaceDetectorSensorLike(FaceSensorLike, Protocol):
    """Protocol for frame-based face detector sensor."""

    @property
    def modelSpec(self) -> ModelSpec:
        """Model specification (input format, output labels, trigger labels)."""
        ...

    async def detectFaces(
        self, frame: VideoFrameData, personRegions: list[Detection] | None = None
    ) -> FaceResult:
        """Detect faces in a frame."""
        ...


class FaceSensor(Sensor[FaceSensorProperties, TStorage, str], Generic[TStorage]):
    """
    Base face sensor for external triggers.

    Use this class when face detection is provided by an external source.
    """

    _requires_frames = False

    def __init__(self, name: str = "Face Sensor") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.detected = False
        self.props.faces = []

    @property
    def type(self) -> SensorType:
        return SensorType.Face

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        """Whether faces are currently detected."""
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        self.props.detected = value

    @property
    def faces(self) -> list[FaceDetection]:
        """Current face detections."""
        return self.props.faces  # type: ignore[no-any-return]

    @faces.setter
    def faces(self, value: list[FaceDetection]) -> None:
        self.props.faces = value


class FaceDetectorSensor(FaceSensor[TStorage], Generic[TStorage]):
    """
    Frame-based face detector.

    Use this class when implementing a face detection plugin.
    Implement the `modelSpec` property to specify input format, output labels, and trigger labels.

    Example:
        ```python
        class MyFaceDetector(FaceDetectorSensor):
            @property
            def modelSpec(self) -> ModelSpec:
                return {
                    "input": {"width": 160, "height": 160, "format": "rgb"},
                    "outputLabels": ["face", "unknown_face"],
                    "triggerLabels": ["person"],  # Triggers on 'person' detections
                }

            async def detectFaces(self, frame, personRegions=None) -> FaceResult:
                ...
        ```
    """

    _requires_frames = True

    @property
    @abstractmethod
    def modelSpec(self) -> ModelSpec:
        """
        Model specification for this face detector.

        Defines:
        - input: Required frame format (width, height, pixel format)
        - outputLabels: Labels this detector outputs (e.g., ['face', 'unknown_face'])
        - triggerLabels: Object labels that trigger face detection (e.g., ['person'])

        The getter is called when the sensor is registered. To change model specs
        at runtime, call requestRestart().
        """
        ...

    @abstractmethod
    async def detectFaces(
        self, frame: VideoFrameData, personRegions: list[Detection] | None = None
    ) -> FaceResult:
        """
        Process frame and return face detection result.

        Args:
            frame: Video frame data
            personRegions: Person regions from ObjectDetectorSensor (matching triggerLabels)

        Returns:
            FaceResult with detected flag and face detections
        """
        ...
