"""Object sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, runtime_checkable

from typing_extensions import TypedDict

from .base import Sensor, SensorLike
from .types import Detection, ObjectClassLabel, SensorCategory, SensorType

if TYPE_CHECKING:
    from ..plugin.interfaces import ObjectResult, VideoFrameData, VideoInputProperties


class ObjectProperty(str, Enum):
    """Object sensor properties."""

    Detected = "detected"
    Detections = "detections"
    Labels = "labels"


class ObjectSensorProperties(TypedDict):
    """Object sensor properties interface."""

    detected: bool
    detections: list[Detection]
    labels: list[ObjectClassLabel]


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class ObjectSensorLike(SensorLike, Protocol):
    """Protocol for object sensor type checking."""

    @property
    def detected(self) -> bool:
        """Whether objects are currently detected."""
        ...

    @property
    def detections(self) -> list[Detection]:
        """Current object detections."""
        ...

    @property
    def labels(self) -> list[ObjectClassLabel]:
        """Detected object labels."""
        ...


@runtime_checkable
class ObjectDetectorSensorLike(ObjectSensorLike, Protocol):
    """Protocol for frame-based object detector sensor."""

    @property
    def inputProperties(self) -> VideoInputProperties:
        """Required input frame properties."""
        ...

    async def detectObjects(self, frame: VideoFrameData) -> ObjectResult:
        """Detect objects in a frame."""
        ...


class ObjectSensor(Sensor[ObjectSensorProperties, TStorage, str], Generic[TStorage]):
    """
    Base object sensor for external triggers (Ring, ONVIF, cloud APIs).

    Use this class when object detection is provided by an external source.
    Properties can be set directly: `sensor.detected = True`

    Example:
        ```python
        class MyObjectSensor(ObjectSensor):
            def __init__(self, device: MyDevice):
                super().__init__("Object Sensor")

                device.on_object_detected.subscribe(lambda result:
                    (setattr(self, 'detected', result.detected),
                     setattr(self, 'detections', result.objects))
                )
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Object Sensor") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.detected = False
        self.props.detections = []
        self.props.labels = []

    @property
    def type(self) -> SensorType:
        return SensorType.Object

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        """Whether objects are currently detected."""
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        """Set object detected state."""
        self.props.detected = value

    @property
    def detections(self) -> list[Detection]:
        """Current object detections."""
        return self.props.detections  # type: ignore[no-any-return]

    @detections.setter
    def detections(self, value: list[Detection]) -> None:
        """Set object detections."""
        self.props.detections = value
        # Auto-update labels from detections
        labels = list({d["label"] for d in value})
        self.props.labels = labels

    @property
    def labels(self) -> list[ObjectClassLabel]:
        """Labels currently being detected."""
        return self.props.labels  # type: ignore[no-any-return]

    @labels.setter
    def labels(self, value: list[ObjectClassLabel]) -> None:
        """Set detected labels."""
        self.props.labels = value


class ObjectDetectorSensor(ObjectSensor):
    """
    Frame-based object detector (TensorFlow, YOLO, etc.).

    Use this class when implementing an object detection plugin that
    processes video frames to detect objects.
    """

    _requires_frames = True

    @property
    @abstractmethod
    def inputProperties(self) -> VideoInputProperties:
        """Define required frame format."""
        ...

    @abstractmethod
    async def detectObjects(self, frame: VideoFrameData) -> ObjectResult:
        """Process frame and return detection result."""
        ...
