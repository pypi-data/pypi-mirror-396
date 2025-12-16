"""Classifier sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import Detection, ModelSpec, SensorCategory, SensorType

if TYPE_CHECKING:
    from ..plugin.interfaces import ClassifierResult, VideoFrameData


class ClassifierProperty(str, Enum):
    """Classifier sensor properties."""

    Detected = "detected"
    Detections = "detections"
    Labels = "labels"


class ClassifierSensorProperties(TypedDict):
    """Classifier sensor properties interface."""

    detected: bool
    detections: list[Detection]
    labels: list[str]


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class ClassifierSensorLike(SensorLike, Protocol):
    """Protocol for classifier sensor type checking."""

    @property
    def detected(self) -> bool:
        """Whether classifications are currently detected."""
        ...

    @property
    def detections(self) -> list[Detection]:
        """Current classification detections."""
        ...

    @property
    def labels(self) -> list[str]:
        """Detected classification labels."""
        ...


@runtime_checkable
class ClassifierDetectorSensorLike(ClassifierSensorLike, Protocol):
    """Protocol for frame-based classifier sensor."""

    @property
    def modelSpec(self) -> ModelSpec:
        """Model specification (input format, output labels, trigger labels)."""
        ...

    async def classify(
        self, frame: VideoFrameData, triggerRegions: list[Detection] | None = None
    ) -> ClassifierResult:
        """Classify objects in a frame."""
        ...


class ClassifierSensor(Sensor[ClassifierSensorProperties, TStorage, str], Generic[TStorage]):
    """
    Base classifier sensor for external classification events.

    Use this class when classification is provided by an external source (cloud APIs, etc.)
    Properties can be set directly: `sensor.detected = True`

    This is a Multi-Provider sensor type - multiple classifiers can be
    registered per camera (e.g., Bird + DogBreed + PlantSpecies).

    Example:
        ```python
        class CloudBirdClassifier(ClassifierSensor):
            def __init__(self, device: MyDevice):
                super().__init__("Bird Classifier")

                device.on_classification.subscribe(lambda result:
                    (setattr(self, 'detected', result.detected),
                     setattr(self, 'detections', result.classifications))
                )
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Classifier") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.detected = False
        self.props.detections = []
        self.props.labels = []

    @property
    def type(self) -> SensorType:
        return SensorType.Classifier

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        """Whether classifications are currently detected."""
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        """Set classification detected state."""
        self.props.detected = value

    @property
    def detections(self) -> list[Detection]:
        """Current classification detections."""
        return self.props.detections  # type: ignore[no-any-return]

    @detections.setter
    def detections(self, value: list[Detection]) -> None:
        """Set classification detections."""
        self.props.detections = value
        # Auto-update labels from detections
        labels = list({d["label"] for d in value})
        self.props.labels = labels

    @property
    def labels(self) -> list[str]:
        """Labels currently being detected."""
        return self.props.labels  # type: ignore[no-any-return]

    @labels.setter
    def labels(self, value: list[str]) -> None:
        """Set detected labels."""
        self.props.labels = value


class ClassifierDetectorSensor(ClassifierSensor[TStorage], Generic[TStorage]):
    """
    Frame-based classifier (TensorFlow classifiers, etc.).

    Use this class when implementing a custom classifier plugin that
    processes video frames to classify objects.

    This is a Multi-Provider sensor type - multiple classifiers can be
    registered per camera (e.g., Bird + DogBreed + PlantSpecies).

    Example:
        ```python
        class BirdClassifier(ClassifierDetectorSensor):
            @property
            def modelSpec(self) -> ModelSpec:
                return {
                    "input": {"width": 224, "height": 224, "format": "rgb"},
                    "outputLabels": ["sparrow", "eagle", "crow", "pigeon", ...],
                    "triggerLabels": ["bird"],  # Triggers on 'bird' from Object Detection
                }

            async def classify(self, frame, triggerRegions=None) -> ClassifierResult:
                ...
        ```
    """

    _requires_frames = True

    @property
    @abstractmethod
    def modelSpec(self) -> ModelSpec:
        """
        Model specification for this classifier.

        Defines:
        - input: Required frame format (width, height, pixel format)
        - outputLabels: Labels this classifier outputs (e.g., bird species)
        - triggerLabels: Object labels that trigger this classifier (e.g., ['bird'])

        The getter is called when the sensor is registered. To change model specs
        at runtime (e.g., after model switch), call requestRestart().
        """
        ...

    @abstractmethod
    async def classify(
        self, frame: VideoFrameData, triggerRegions: list[Detection] | None = None
    ) -> ClassifierResult:
        """
        Classify objects in a frame.

        Args:
            frame: Video frame data
            triggerRegions: Regions from Object Detection (matching triggerLabels)

        Returns:
            ClassifierResult with detected flag and classification detections
        """
        ...
