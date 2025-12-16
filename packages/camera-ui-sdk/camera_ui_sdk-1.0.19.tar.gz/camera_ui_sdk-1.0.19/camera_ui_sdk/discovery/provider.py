"""Discovery provider interface and base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .types import DiscoveredCamera, DiscoveryStatus

if TYPE_CHECKING:
    from ..camera.config import CameraConfig
    from ..storage.schema import JsonSchemaWithoutCallbacks


class DiscoveryProvider(ABC):
    """Discovery provider interface for cameraController plugins.

    Implement this class in your cameraController plugin to provide
    camera discovery functionality.

    Example:
        ```python
        class OnvifDiscoveryProvider(BaseDiscoveryProvider):
            @property
            def name(self) -> str:
                return "ONVIF"

            @property
            def description(self) -> str | None:
                return "Discover ONVIF-compatible cameras"

            async def startDiscovery(self) -> None:
                self._status = DiscoveryStatus.Scanning
                # Start WS-Discovery probe...

            async def stopDiscovery(self) -> None:
                self._status = DiscoveryStatus.Stopped

            async def getConnectionSchema(
                self, camera: DiscoveredCamera
            ) -> list[JsonSchemaWithoutCallbacks]:
                return [
                    {"key": "username", "type": "string", "title": "Username", "description": "Camera username"},
                    {"key": "password", "type": "string", "title": "Password", "description": "Camera password", "format": "password"},
                ]

            async def createCameraConfig(
                self, camera: DiscoveredCamera, connectionConfig: dict[str, object]
            ) -> CameraConfig:
                # Probe ONVIF device and return config
                ...
        ```
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider display name."""
        ...

    @property
    def description(self) -> str | None:
        """Provider description."""
        return None

    @abstractmethod
    async def startDiscovery(self) -> None:
        """Start continuous discovery scanning.

        Plugin should store cameras internally; backend will poll via getDiscoveredCameras().
        """
        ...

    @abstractmethod
    async def stopDiscovery(self) -> None:
        """Stop discovery scanning."""
        ...

    async def rescan(self) -> None:
        """Trigger a single rescan (for manual refresh).

        Returns when scan is complete. Override this method if your
        provider supports manual rescan.
        """
        pass

    @abstractmethod
    def getStatus(self) -> DiscoveryStatus:
        """Get current discovery status."""
        ...

    @abstractmethod
    def getDiscoveredCameras(self) -> list[DiscoveredCamera]:
        """Get all currently discovered cameras."""
        ...

    @abstractmethod
    async def getConnectionSchema(
        self, camera: DiscoveredCamera
    ) -> list[JsonSchemaWithoutCallbacks]:
        """Get connection schema for a specific discovered camera.

        Returns JsonSchema array for dynamic form generation.

        Args:
            camera: The discovered camera

        Returns:
            List of schema fields for connection configuration
        """
        ...

    @abstractmethod
    async def createCameraConfig(
        self, camera: DiscoveredCamera, connectionConfig: dict[str, object]
    ) -> CameraConfig:
        """Create camera configuration from discovered camera + user input.

        Called when user clicks "Connect" with filled form.

        Args:
            camera: The discovered camera
            connectionConfig: User-provided configuration from schema form

        Returns:
            CameraConfig ready for DeviceManager.createCamera()
        """
        ...


class BaseDiscoveryProvider(DiscoveryProvider):
    """Base class for DiscoveryProvider with helper methods.

    Provides default implementations and helper methods for common
    discovery provider operations.

    Example:
        ```python
        class MyDiscoveryProvider(BaseDiscoveryProvider):
            @property
            def name(self) -> str:
                return "My Discovery"

            async def startDiscovery(self) -> None:
                self._status = DiscoveryStatus.Scanning
                # When a camera is found:
                self._addCamera({
                    "id": "camera-1",
                    "name": "My Camera",
                    "address": "192.168.1.100",
                    "discoveredAt": int(time.time() * 1000),
                })

            async def stopDiscovery(self) -> None:
                self._status = DiscoveryStatus.Stopped

            async def getConnectionSchema(self, camera):
                return [...]

            async def createCameraConfig(self, camera, config):
                return {...}
        ```
    """

    def __init__(self) -> None:
        """Initialize the base discovery provider."""
        self._status: DiscoveryStatus = DiscoveryStatus.Idle
        self._cameras: dict[str, DiscoveredCamera] = {}

    def getStatus(self) -> DiscoveryStatus:
        """Get current discovery status."""
        return self._status

    def getDiscoveredCameras(self) -> list[DiscoveredCamera]:
        """Get all currently discovered cameras."""
        return list(self._cameras.values())

    def _addCamera(self, camera: DiscoveredCamera) -> None:
        """Add or update a discovered camera.

        Args:
            camera: The discovered camera to add
        """
        camera_id = camera.get("id", "")
        self._cameras[camera_id] = camera

    def _removeCamera(self, cameraId: str) -> None:
        """Remove a camera (went offline).

        Args:
            cameraId: The ID of the camera to remove
        """
        if cameraId in self._cameras:
            del self._cameras[cameraId]

    def _clearCameras(self) -> None:
        """Clear all discovered cameras."""
        self._cameras.clear()
