"""License plate sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import Detection, LicensePlateDetection, ModelSpec, SensorCategory, SensorType

if TYPE_CHECKING:
    from ..plugin.interfaces import LicensePlateResult, VideoFrameData


class LicensePlateProperty(str, Enum):
    """License plate sensor properties."""

    Detected = "detected"
    Plates = "plates"


class LicensePlateSensorProperties(TypedDict):
    """License plate sensor properties interface."""

    detected: bool
    plates: list[LicensePlateDetection]


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class LicensePlateSensorLike(SensorLike, Protocol):
    """Protocol for license plate sensor type checking."""

    @property
    def detected(self) -> bool:
        """Whether license plates are currently detected."""
        ...

    @property
    def plates(self) -> list[LicensePlateDetection]:
        """Current license plate detections."""
        ...


@runtime_checkable
class LicensePlateDetectorSensorLike(LicensePlateSensorLike, Protocol):
    """Protocol for frame-based license plate detector sensor."""

    @property
    def modelSpec(self) -> ModelSpec:
        """Model specification (input format, output labels, trigger labels)."""
        ...

    async def detectLicensePlates(
        self, frame: VideoFrameData, vehicleRegions: list[Detection] | None = None
    ) -> LicensePlateResult:
        """Detect license plates in a frame."""
        ...


class LicensePlateSensor(Sensor[LicensePlateSensorProperties, TStorage, str], Generic[TStorage]):
    """
    Base license plate sensor for external triggers.

    Use this class when license plate detection is provided by an external source.
    """

    _requires_frames = False

    def __init__(self, name: str = "License Plate Sensor") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.detected = False
        self.props.plates = []

    @property
    def type(self) -> SensorType:
        return SensorType.LicensePlate

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        """Whether license plates are currently detected."""
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        self.props.detected = value

    @property
    def plates(self) -> list[LicensePlateDetection]:
        """Current license plate detections."""
        return self.props.plates  # type: ignore[no-any-return]

    @plates.setter
    def plates(self, value: list[LicensePlateDetection]) -> None:
        self.props.plates = value


class LicensePlateDetectorSensor(LicensePlateSensor[TStorage], Generic[TStorage]):
    """
    Frame-based license plate detector (OCR).

    Use this class when implementing a license plate detection plugin.
    Implement the `modelSpec` property to specify input format, output labels, and trigger labels.

    Example:
        ```python
        class MyLPRDetector(LicensePlateDetectorSensor):
            @property
            def modelSpec(self) -> ModelSpec:
                return {
                    "input": {"width": 320, "height": 160, "format": "rgb"},
                    "outputLabels": ["license_plate"],
                    "triggerLabels": ["car", "truck", "bus", "motorcycle"],
                }

            async def detectLicensePlates(self, frame, vehicleRegions=None) -> LicensePlateResult:
                ...
        ```
    """

    _requires_frames = True

    @property
    @abstractmethod
    def modelSpec(self) -> ModelSpec:
        """
        Model specification for this license plate detector.

        Defines:
        - input: Required frame format (width, height, pixel format)
        - outputLabels: Labels this detector outputs (e.g., ['license_plate'])
        - triggerLabels: Object labels that trigger LPD (e.g., ['car', 'truck', 'bus', 'motorcycle'])

        The getter is called when the sensor is registered. To change model specs
        at runtime, call requestRestart().
        """
        ...

    @abstractmethod
    async def detectLicensePlates(
        self, frame: VideoFrameData, vehicleRegions: list[Detection] | None = None
    ) -> LicensePlateResult:
        """
        Process frame and return license plate detection result.

        Args:
            frame: Video frame data
            vehicleRegions: Vehicle regions from ObjectDetectorSensor (matching triggerLabels)

        Returns:
            LicensePlateResult with detected flag and plate detections
        """
        ...
