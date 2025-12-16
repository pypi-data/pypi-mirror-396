"""Audio sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import Detection, SensorCategory, SensorType

if TYPE_CHECKING:
    from ..plugin.interfaces import AudioFrameData, AudioInputProperties, AudioResult


class AudioProperty(str, Enum):
    """Audio sensor properties."""

    Detected = "detected"
    Detections = "detections"
    Decibels = "decibels"


class AudioSensorProperties(TypedDict):
    """Audio sensor properties interface."""

    detected: bool
    detections: list[Detection]
    decibels: float


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class AudioSensorLike(SensorLike, Protocol):
    """Protocol for audio sensor type checking."""

    @property
    def detected(self) -> bool:
        """Whether audio is currently detected."""
        ...

    @property
    def detections(self) -> list[Detection]:
        """Current audio detections."""
        ...

    @property
    def decibels(self) -> float:
        """Current decibel level."""
        ...


@runtime_checkable
class AudioDetectorSensorLike(AudioSensorLike, Protocol):
    """Protocol for frame-based audio detector sensor."""

    @property
    def inputProperties(self) -> AudioInputProperties:
        """Required input audio properties."""
        ...

    async def detectAudio(self, audio: AudioFrameData) -> AudioResult:
        """Detect audio events."""
        ...


class AudioSensor(Sensor[AudioSensorProperties, TStorage, str], Generic[TStorage]):
    """
    Base audio sensor for external triggers (Ring, ONVIF).

    Use this class when audio detection is provided by an external source.
    Properties can be set directly: `sensor.detected = True`

    Example:
        ```python
        class MyAudioSensor(AudioSensor):
            def __init__(self, device: MyDevice):
                super().__init__("Audio Sensor")

                device.on_audio_event.subscribe(lambda event:
                    (setattr(self, 'detected', event.detected),
                     setattr(self, 'decibels', event.level))
                )
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Audio Sensor") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.detected = False
        self.props.detections = []
        self.props.decibels = 0.0

    @property
    def type(self) -> SensorType:
        return SensorType.Audio

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        """Whether audio event is currently detected."""
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        """Set audio detected state."""
        self.props.detected = value

    @property
    def detections(self) -> list[Detection]:
        """Current audio detections."""
        return self.props.detections  # type: ignore[no-any-return]

    @detections.setter
    def detections(self, value: list[Detection]) -> None:
        """Set audio detections."""
        self.props.detections = value

    @property
    def decibels(self) -> float:
        """Current decibel level."""
        return self.props.decibels  # type: ignore[no-any-return]

    @decibels.setter
    def decibels(self, value: float) -> None:
        """Set decibel level."""
        self.props.decibels = value


class AudioDetectorSensor(AudioSensor):
    """
    Frame-based audio detector (glass break detection, etc.).

    Use this class when implementing an audio detection plugin that
    processes audio frames.
    """

    _requires_frames = True

    @property
    @abstractmethod
    def inputProperties(self) -> AudioInputProperties:
        """Define required audio format."""
        ...

    @abstractmethod
    async def detectAudio(self, audio: AudioFrameData) -> AudioResult:
        """Process audio and return detection result."""
        ...
