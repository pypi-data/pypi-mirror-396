"""Plugin types and interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypedDict, runtime_checkable

from ..sensor.types import Detection
from ..storage.schema import JsonSchema

if TYPE_CHECKING:
    from ..camera.device import CameraDevice
    from ..camera.types import PythonVersion
    from ..manager.types import CoreManager, DeviceManager, DiscoveryManager, LoggerService
    from ..storage.storages import DeviceStorage, StorageController

APIEventType = Literal["finishLaunching", "shutdown"]

APIListener = Callable[[], None] | Callable[[], Awaitable[None]]


class PluginRole(StrEnum):
    """Plugin Role - Defines what a plugin can do.

    - Hub: Only consumes sensors, cannot create cameras or provide sensors
    - SensorProvider: Provides sensors to ANY camera, cannot create cameras
    - CameraController: Creates cameras, provides sensors only to its OWN cameras
    - CameraAndSensorProvider: Creates cameras AND provides sensors to ANY camera
    """

    HUB = "hub"
    """Hub plugins only consume sensors. Cannot create cameras or provide sensors."""

    SENSOR_PROVIDER = "sensorProvider"
    """Sensor provider plugins provide sensors to ANY camera. Cannot create cameras."""

    CAMERA_CONTROLLER = "cameraController"
    """Camera controller plugins create cameras and provide sensors only to their OWN cameras."""

    CAMERA_AND_SENSOR_PROVIDER = "cameraAndSensorProvider"
    """Camera and sensor provider plugins create cameras AND provide sensors to ANY camera."""


class PluginContract(TypedDict, total=False):
    """Plugin contract configuration.

    Every plugin must declare its role, what sensors it provides and consumes.
    """

    role: str  # PluginRole value
    provides: list[str]  # SensorType values
    consumes: list[str]  # SensorType values
    name: str
    pythonVersion: PythonVersion
    dependencies: list[str]


class PluginInfo(TypedDict):
    """Plugin information."""

    id: str
    name: str
    contract: PluginContract


class ImageMetadata(TypedDict):
    """Image metadata for test functions."""

    width: int
    height: int


class AudioMetadata(TypedDict):
    """Audio metadata for test functions."""

    mimeType: str  # 'audio/mpeg' | 'audio/wav' | 'audio/ogg'


class MotionDetectionPluginResponse(TypedDict, total=False):
    """Motion detection test response."""

    detected: bool
    detections: list[Detection]
    videoData: bytes


class ObjectDetectionPluginResponse(TypedDict):
    """Object detection test response."""

    detected: bool
    detections: list[Detection]


class AudioDetectionPluginResponse(TypedDict, total=False):
    """Audio detection test response."""

    detected: bool
    detections: list[Detection]
    decibels: float


@runtime_checkable
class PluginAPI(Protocol):
    """Plugin API - injected into plugins at runtime."""

    @property
    def coreManager(self) -> CoreManager:
        """Core manager for system operations."""
        ...

    @property
    def deviceManager(self) -> DeviceManager:
        """Device manager for camera operations."""
        ...

    @property
    def discoveryManager(self) -> DiscoveryManager:
        """Discovery manager for camera discovery (CameraController/CameraAndSensorProvider roles only)."""
        ...

    @property
    def storageController(self) -> StorageController:
        """Storage controller for persistent storage."""
        ...

    @property
    def storagePath(self) -> str:
        """Path to plugin storage directory."""
        ...

    def on(self, event: APIEventType, f: APIListener) -> Any:
        """
        Subscribe to an event.

        Args:
            event: Event name ('finishLaunching' or 'shutdown')
            listener: Event listener (sync or async)

        Returns:
            Self for chaining
        """
        ...

    def once(self, event: APIEventType, f: APIListener) -> Any:
        """
        Subscribe to an event once.

        Args:
            event: Event name
            listener: Event listener (sync or async)

        Returns:
            Self for chaining
        """
        ...

    def off(self, event: APIEventType, f: APIListener) -> None:
        """
        Unsubscribe from an event.

        Args:
            event: Event name
            listener: Event listener (sync or async)

        Returns:
            Self for chaining
        """
        ...

    def removeListener(self, event: APIEventType, f: APIListener) -> None:
        """
        Remove a listener.

        Args:
            event: Event name
            listener: Event listener (sync or async)

        Returns:
            Self for chaining
        """
        ...

    def removeAllListeners(self, event: APIEventType | None = None) -> None:
        """
        Remove all listeners.

        Args:
            event: Optional event name to remove listeners for

        Returns:
            Self for chaining
        """
        ...


class CuiPlugin(ABC):
    """
    Base plugin class - all plugins must extend this.

    Args:
        logger: Logger service for this plugin
        api: Plugin API for accessing system services
        storage: Plugin storage for configuration

    Example:
        ```python
        class MyPlugin(CuiPlugin):
            def __init__(self, logger: LoggerService, api: PluginAPI, storage: DeviceStorage) -> None:
                super().__init__(logger, api, storage)
                self.my_cameras = {}

            async def configureCameras(self, cameras: list[CameraDevice]) -> None:
                self.logger.log("Starting...")
        ```
    """

    def __init__(self, logger: LoggerService, api: PluginAPI, storage: DeviceStorage) -> None:
        """
        Initialize the plugin.

        Args:
            logger: Logger service for this plugin
            api: Plugin API for accessing system services
            storage: Plugin storage for configuration
        """
        self.logger = logger
        self.api = api
        self.storage = storage

    @abstractmethod
    async def configureCameras(self, camera_devices: list[CameraDevice]) -> None:
        """
        Configure cameras for this plugin.

        Called when cameras are available for the plugin to configure.
        Add sensors, services, and set up event handlers here.

        Args:
            cameras: List of camera devices assigned to this plugin
        """
        ...

    async def interfaceSchema(self) -> list[JsonSchema] | None:
        """
        Return interface schema for plugin configuration UI.

        Override this method to provide a configuration UI schema.

        Returns:
            List of JSON schemas for configuration or None
        """
        return None

    async def testMotion(
        self, video_data: bytes, config: dict[str, Any]
    ) -> MotionDetectionPluginResponse | None:
        """
        Test motion detection with video data.

        Override this method to support motion detection testing.

        Args:
            videoData: Video data to test
            config: Plugin configuration

        Returns:
            Motion detection response or None
        """
        return None

    async def testObjects(
        self, image_data: bytes, metadata: ImageMetadata, config: dict[str, Any]
    ) -> ObjectDetectionPluginResponse | None:
        """
        Test object detection with image data.

        Override this method to support object detection testing.

        Args:
            imageData: Image data to test
            metadata: Image metadata
            config: Plugin configuration

        Returns:
            Object detection response or None
        """
        return None

    async def testAudio(
        self, audio_data: bytes, metadata: AudioMetadata, config: dict[str, Any]
    ) -> AudioDetectionPluginResponse | None:
        """
        Test audio detection with audio data.

        Override this method to support audio detection testing.

        Args:
            audioData: Audio data to test
            metadata: Audio metadata
            config: Plugin configuration

        Returns:
            Audio detection response or None
        """
        return None
