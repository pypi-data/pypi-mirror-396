"""Camera device protocol and types."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypedDict, runtime_checkable

from .config import (
    CameraFrameWorkerSettings,
    CameraInformation,
    CameraRecordingSettings,
    CameraSource,
    CameraSourceData,
    CameraUiSettings,
)
from .detection import CameraDetectionSettings, DetectionZone
from .types import CameraType

if TYPE_CHECKING:
    from ..camera.streaming import RTSPUrlOptions
    from ..manager.types import LoggerService
    from ..observable import HybridObservable
    from ..sensor.base import Sensor, SensorLike
    from ..sensor.types import Detection, SensorType
    from ..service.base import Service, ServiceType


class AssignedPlugin(TypedDict):
    """Assigned plugin information."""

    id: str
    name: str


class PluginAssignments(TypedDict, total=False):
    """Plugin assignments for a camera - maps sensor types to assigned plugins."""

    # Single provider - Detection (only 1 plugin can process frames)
    motion: AssignedPlugin
    object: AssignedPlugin
    audio: AssignedPlugin
    face: AssignedPlugin
    licensePlate: AssignedPlugin

    # Single provider - Special
    ptz: AssignedPlugin
    battery: AssignedPlugin
    cameraController: AssignedPlugin

    # Multiple provider - Controls (external hardware)
    light: list[AssignedPlugin]
    siren: list[AssignedPlugin]

    # Multiple provider - Triggers/Sensors (external hardware)
    contact: list[AssignedPlugin]
    doorbell: list[AssignedPlugin]

    # Multiple provider - Integration
    hub: list[AssignedPlugin]


class CameraPluginInfo(TypedDict):
    """Camera plugin info."""

    id: str
    name: str


class BaseCamera(TypedDict):
    """Base camera properties."""

    _id: str
    nativeId: str | None
    pluginInfo: CameraPluginInfo | None
    name: str
    disabled: bool
    isCloud: bool
    info: CameraInformation
    type: CameraType
    snapshotTTL: int
    detectionZones: list[DetectionZone]
    detectionSettings: CameraDetectionSettings
    frameWorkerSettings: CameraFrameWorkerSettings
    interface: CameraUiSettings
    recording: CameraRecordingSettings
    plugins: list[AssignedPlugin]
    assignments: PluginAssignments


class Camera(BaseCamera):
    """Full camera with sources."""

    sources: list[CameraSourceData]


# See Camera
CameraPublicProperties = Literal[
    "_id",
    "nativeId",
    "pluginInfo",
    "name",
    "disabled",
    "isCloud",
    "info",
    "type",
    "snapshotTTL",
    "detectionZones",
    "detectionSettings",
    "frameWorkerSettings",
    "interface",
    "recording",
    "plugins",
    "assignments",
    "sources",
]


class CameraPropertyObservableObject(TypedDict):
    property: str
    old_state: Any
    new_state: Any


@runtime_checkable
class CameraDeviceSource(CameraSource, Protocol):
    def generateRTSPUrl(self, options: RTSPUrlOptions | None = None) -> str:
        """Generate RTSP URL with given options."""
        ...


@runtime_checkable
class CameraDevice(Protocol):
    """
    Camera Device - Main interface for plugin developers.

    This protocol defines the interface that plugins use to interact with cameras.
    """

    @property
    def id(self) -> str:
        """Camera ID."""
        ...

    @property
    def nativeId(self) -> str | None:
        """Native ID from the camera/plugin."""
        ...

    @property
    def pluginInfo(self) -> CameraPluginInfo | None:
        """Plugin info if camera was created by a plugin."""
        ...

    @property
    def disabled(self) -> bool:
        """Whether the camera is disabled."""
        ...

    @property
    def name(self) -> str:
        """Camera name."""
        ...

    @property
    def type(self) -> CameraType:
        """Camera type (camera or doorbell)."""
        ...

    @property
    def snapshotTTL(self) -> int:
        """Snapshot time-to-live in seconds."""
        ...

    @property
    def info(self) -> CameraInformation:
        """Camera information metadata."""
        ...

    @property
    def isCloud(self) -> bool:
        """Whether this is a cloud camera."""
        ...

    @property
    def detectionZones(self) -> list[DetectionZone]:
        """Detection zones configured for this camera."""
        ...

    @property
    def detectionSettings(self) -> CameraDetectionSettings:
        """Detection settings for this camera."""
        ...

    @property
    def frameWorkerSettings(self) -> CameraFrameWorkerSettings:
        """Frame worker settings."""
        ...

    @property
    def sources(self) -> list[CameraDeviceSource]:
        """All camera sources."""
        ...

    @property
    def streamSource(self) -> CameraDeviceSource:
        """Primary stream source for this camera."""
        ...

    @property
    def highResolutionSource(self) -> CameraDeviceSource | None:
        """High resolution stream source for this camera, if available."""
        ...

    @property
    def midResolutionSource(self) -> CameraDeviceSource | None:
        """Mid resolution stream source for this camera, if available."""
        ...

    @property
    def lowResolutionSource(self) -> CameraDeviceSource | None:
        """Low resolution stream source for this camera, if available."""
        ...

    @property
    def snapshotSource(self) -> CameraSource | None:
        """Snapshot source for this camera, if available."""
        ...

    @property
    def connected(self) -> bool:
        """Whether the camera is connected."""
        ...

    @property
    def frameWorkerConnected(self) -> bool:
        """Whether the frame worker is connected."""
        ...

    @property
    def onConnected(self) -> HybridObservable[bool]:
        """Subscribe to camera connected events."""
        ...

    @property
    def onFrameWorkerConnected(self) -> HybridObservable[bool]:
        """Subscribe to frame worker connected events."""
        ...

    @property
    def logger(self) -> LoggerService:
        """Logger service for this camera."""
        ...

    async def connect(self) -> None:
        """Connect to the camera."""
        ...

    async def disconnect(self) -> None:
        """Disconnect from the camera."""
        ...

    def onPropertyChange(
        self, property: CameraPublicProperties | list[CameraPublicProperties]
    ) -> HybridObservable[CameraPropertyObservableObject]: ...

    # Sensor-based Architecture

    def getSensors(self) -> list[SensorLike]:
        """Get all sensors for this camera."""
        ...

    def getSensor(self, sensorId: str) -> SensorLike | None:
        """Get a sensor by ID."""
        ...

    def getSensorsByType(self, sensorType: SensorType) -> list[SensorLike]:
        """Get all sensors of a specific type."""
        ...

    # Typed Sensor Getters (stable across plugin switches)

    def getMotionSensor(self) -> SensorLike | None:
        """Get the motion sensor (stable across plugin switches)."""
        ...

    def getObjectSensor(self) -> SensorLike | None:
        """Get the object sensor (stable across plugin switches)."""
        ...

    def getFaceSensor(self) -> SensorLike | None:
        """Get the face sensor (stable across plugin switches)."""
        ...

    def getLicensePlateSensor(self) -> SensorLike | None:
        """Get the license plate sensor (stable across plugin switches)."""
        ...

    def getAudioSensor(self) -> SensorLike | None:
        """Get the audio sensor (stable across plugin switches)."""
        ...

    def getPTZControl(self) -> SensorLike | None:
        """Get the PTZ control (stable across plugin switches)."""
        ...

    async def addSensor(self, sensor: Sensor[Any, Any, Any]) -> None:
        """Add a sensor to this camera."""
        ...

    async def removeSensor(self, sensorId: str) -> None:
        """Remove a sensor from this camera."""
        ...

    def onSensorAdded(self, callback: Callable[[str, SensorType], None]) -> Callable[[], None]:
        """
        Subscribe to sensor added events.

        Args:
            callback: Callback receiving (sensorId, sensorType)

        Returns:
            Unsubscribe function

        Note:
            Use getSensor(sensorId) to get the full sensor if needed.
        """
        ...

    def onSensorRemoved(self, callback: Callable[[str, SensorType], None]) -> Callable[[], None]:
        """
        Subscribe to sensor removed events.

        Args:
            callback: Callback receiving (sensorId, sensorType)

        Returns:
            Unsubscribe function
        """
        ...

    # Service Methods

    async def registerService(self, service: Service) -> None:
        """Register a service for this camera."""
        ...

    async def unregisterService(self, serviceType: ServiceType) -> None:
        """Unregister a service from this camera."""
        ...
