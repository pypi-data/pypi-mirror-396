"""Motion sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import Detection, SensorCategory, SensorType

if TYPE_CHECKING:
    from ..plugin.interfaces import MotionResult, VideoFrameData


class MotionProperty(str, Enum):
    """Motion sensor properties."""

    Detected = "detected"
    Detections = "detections"
    Blocked = "blocked"


class MotionSensorProperties(TypedDict):
    """Motion sensor properties interface."""

    detected: bool
    detections: list[Detection]
    blocked: bool


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class MotionSensorLike(SensorLike, Protocol):
    """Protocol for motion sensor type checking."""

    @property
    def detected(self) -> bool:
        """Whether motion is currently detected."""
        ...

    @property
    def detections(self) -> list[Detection]:
        """Current motion detections."""
        ...

    @property
    def blocked(self) -> bool:
        """Whether the sensor is blocked (read-only, managed by backend)."""
        ...


@runtime_checkable
class MotionDetectorSensorLike(MotionSensorLike, Protocol):
    """Protocol for frame-based motion detector sensor."""

    async def detectMotion(self, frame: VideoFrameData) -> MotionResult:
        """Detect motion in a frame."""
        ...


class MotionSensor(Sensor[MotionSensorProperties, TStorage, str], Generic[TStorage]):
    """
    Base motion sensor for external triggers (Ring, ONVIF, SMTP).

    Use this class when motion detection is provided by an external source
    (e.g., camera firmware, cloud service, or SMTP notifications).

    Example:
        ```python
        class RingMotionSensor(MotionSensor):
            def __init__(self, ring_camera: RingCamera):
                super().__init__("Ring Motion")

                ring_camera.on_motion_detected.subscribe(lambda detected:
                    setattr(self, 'detected', detected)
                )
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Motion Sensor") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.detected = False
        self.props.detections = []
        self.props.blocked = False

    @property
    def type(self) -> SensorType:
        return SensorType.Motion

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        """Whether motion is currently detected."""
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        """Set motion detected state (ignored if sensor is blocked)."""
        if self.props.blocked:
            return
        self.props.detected = value

    @property
    def detections(self) -> list[Detection]:
        """Current motion detections."""
        return self.props.detections  # type: ignore[no-any-return]

    @detections.setter
    def detections(self, value: list[Detection]) -> None:
        """Set motion detections (ignored if sensor is blocked)."""
        if self.props.blocked:
            return
        self.props.detections = value

    @property
    def blocked(self) -> bool:
        """
        Whether the sensor is currently blocked (read-only).

        When blocked, state changes are ignored by the backend during dwell time.
        This is managed by the backend - plugins cannot set this.
        """
        return self.props.blocked  # type: ignore[no-any-return]


class MotionDetectorSensor(MotionSensor[TStorage], Generic[TStorage]):
    """
    Frame-based motion detector (rust-motion, OpenCV, etc.).

    Use this class when implementing a motion detection plugin that
    processes video frames to detect motion.

    The backend controls the frame resolution via `motionResolution` setting (low/medium/high).
    Frames are always delivered in grayscale format with aspect ratio preserved.

    Example:
        ```python
        class RustMotionSensor(MotionDetectorSensor):
            def __init__(self):
                super().__init__("Rust Motion")

            async def detectMotion(self, frame: VideoFrameData) -> MotionResult:
                # frame.format is always 'gray'
                # frame.width/height are determined by motionResolution setting
                ...
        ```
    """

    _requires_frames = True

    @abstractmethod
    async def detectMotion(self, frame: VideoFrameData) -> MotionResult:
        """
        Process frame and return detection result.

        Note: Frame resolution is controlled by the backend via `motionResolution` setting.
        Frames are always delivered in grayscale ('gray') format.

        Args:
            frame: Video frame data (grayscale, resolution determined by backend)

        Returns:
            MotionResult with detected flag and detection regions
        """
        ...
