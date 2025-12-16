"""Manager types and interfaces."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypedDict, runtime_checkable

if TYPE_CHECKING:
    from ..camera.config import CameraConfig
    from ..camera.device import Camera, CameraDevice
    from ..camera.types import HwAccelMethod
    from ..discovery.provider import DiscoveryProvider
    from ..discovery.types import DiscoveredCamera
    from ..plugin.types import CuiPlugin, PluginInfo


# Event types
DeviceManagerEventType = Literal["cameraSelected", "cameraDeselected"]

# Listener types for DeviceManager events
DeviceManagerSelectedListener = (
    Callable[["CameraDevice"], None] | Callable[["CameraDevice"], Awaitable[None]]
)
DeviceManagerDeselectedListener = Callable[[str], None] | Callable[[str], Awaitable[None]]
DeviceManagerListener = DeviceManagerSelectedListener | DeviceManagerDeselectedListener


# RPC interface for DeviceManager
class DeviceManagerRPC(Protocol):
    """RPC interface for DeviceManager calls from plugins."""

    async def createCamera(self, cameraConfig: CameraConfig, pluginId: str) -> Camera:
        """Create a new camera."""
        ...

    async def updateCamera(self, cameraIdOrName: str, cameraConfig: dict[str, Any], pluginId: str) -> Camera:
        """Update a camera configuration."""
        ...

    async def getCamera(self, cameraIdOrName: str, pluginId: str) -> Camera | None:
        """Get a camera by ID or name."""
        ...

    async def removeCamera(self, cameraIdOrName: str, pluginId: str) -> None:
        """Remove a camera."""
        ...


# RPC interface for CoreManager
class CoreManagerRPC(Protocol):
    """RPC interface for CoreManager calls from plugins."""

    async def getPlugin(self, pluginName: str) -> PluginInfo | None:
        """Get plugin info by name."""
        ...

    async def getFFmpegPath(self) -> str:
        """Get FFmpeg executable path."""
        ...

    async def getHwaccelInfo(self, options: HWAccelOptions) -> list[FfmpegArgs]:
        """Get hardware acceleration information."""
        ...

    async def getServerAddresses(self) -> list[str]:
        """Get server addresses."""
        ...


class LoggerService(Protocol):
    """Logger service interface."""

    def log(self, *args: Any) -> None:
        """Log a message."""
        ...

    def error(self, *args: Any) -> None:
        """Log an error."""
        ...

    def warn(self, *args: Any) -> None:
        """Log a warning."""
        ...

    def success(self, *args: Any) -> None:
        """Log a success message."""
        ...

    def debug(self, *args: Any) -> None:
        """Log a debug message."""
        ...

    def trace(self, *args: Any) -> None:
        """Log a trace message."""
        ...

    def attention(self, *args: Any) -> None:
        """Log an attention message."""
        ...


@runtime_checkable
class DeviceManager(Protocol):
    """Device manager for camera operations."""

    async def createCamera(self, cameraConfig: CameraConfig) -> CameraDevice:
        """
        Create a new camera.

        Args:
            cameraConfig: Camera configuration

        Returns:
            The created camera device
        """
        ...

    async def updateCamera(self, cameraIdOrName: str, cameraConfig: dict[str, Any]) -> CameraDevice:
        """
        Update a camera configuration.

        Args:
            cameraIdOrName: Camera ID or name
            cameraConfig: Partial camera configuration to update

        Returns:
            The updated camera device
        """
        ...

    async def getCamera(self, cameraIdOrName: str) -> CameraDevice | None:
        """
        Get a camera by ID or name.

        Args:
            cameraIdOrName: Camera ID or name

        Returns:
            The camera device or None if not found
        """
        ...

    async def removeCamera(self, cameraIdOrName: str) -> None:
        """
        Remove a camera.

        Args:
            cameraIdOrName: Camera ID or name
        """
        ...

    def on(self, event: DeviceManagerEventType, listener: DeviceManagerListener) -> Any:
        """
        Subscribe to an event.

        Args:
            event: Event name ('cameraSelected' or 'cameraDeselected')
            listener: Event listener

        Returns:
            Self for chaining
        """
        ...

    def once(self, event: DeviceManagerEventType, listener: DeviceManagerListener) -> Any:
        """
        Subscribe to an event once.

        Args:
            event: Event name
            listener: Event listener

        Returns:
            Self for chaining
        """
        ...

    def off(self, event: DeviceManagerEventType, listener: DeviceManagerListener) -> None:
        """
        Unsubscribe from an event.

        Args:
            event: Event name
            listener: Event listener

        Returns:
            Self for chaining
        """
        ...

    def removeListener(self, event: DeviceManagerEventType, listener: DeviceManagerListener) -> None:
        """
        Remove a listener.

        Args:
            event: Event name
            listener: Event listener

        Returns:
            Self for chaining
        """
        ...

    def removeAllListeners(self, event: DeviceManagerEventType | None = None) -> None:
        """
        Remove all listeners.

        Args:
            event: Optional event name to remove listeners for

        Returns:
            Self for chaining
        """
        ...


class HWAccelOptions(TypedDict, total=False):
    """Hardware acceleration options."""

    targetCodec: str  # 'h264' | 'h265'
    keepOnHardware: bool
    pixelFormat: str
    scale: dict[str, int]  # {width: int, height: int}


class FfmpegArgs(TypedDict):
    """FFmpeg arguments for hardware acceleration."""

    codec: str
    hwaccel: HwAccelMethod
    hwaccelArgs: list[str]
    hwaccelFilters: list[str]
    hwDeviceArgs: list[str]
    supported: bool


@runtime_checkable
class CoreManager(Protocol):
    """Core manager for system operations."""

    async def connectToPlugin(self, pluginName: str) -> CuiPlugin | None:
        """
        Connect to another plugin.

        Args:
            pluginName: Name of the plugin to connect to

        Returns:
            The plugin instance or None if not found
        """
        ...

    async def getFFmpegPath(self) -> str:
        """
        Get the FFmpeg executable path.

        Returns:
            Path to FFmpeg
        """
        ...

    async def getHwaccelInfo(self, options: HWAccelOptions) -> list[FfmpegArgs]:
        """
        Get hardware acceleration information.

        Args:
            options: Hardware acceleration options

        Returns:
            List of FFmpeg argument configurations
        """
        ...

    async def getServerAddresses(self) -> list[str]:
        """
        Get server addresses.

        Returns:
            List of server addresses
        """
        ...


# RPC interface for DiscoveryManager
class DiscoveryManagerRPC(Protocol):
    """RPC interface for DiscoveryManager calls from plugins."""

    async def registerProvider(
        self, providerInfo: dict[str, Any], pluginId: str
    ) -> None:
        """Register a discovery provider."""
        ...

    async def unregisterProvider(self, pluginId: str) -> None:
        """Unregister the discovery provider."""
        ...

    async def startDiscovery(self, pluginId: str) -> None:
        """Start discovery scanning."""
        ...

    async def stopDiscovery(self, pluginId: str) -> None:
        """Stop discovery scanning."""
        ...

    async def rescan(self, pluginId: str) -> None:
        """Trigger a manual rescan."""
        ...

    async def getDiscoveredCameras(self, pluginId: str) -> list[DiscoveredCamera]:
        """Get discovered cameras."""
        ...

    async def notifyCameraDiscovered(
        self, camera: DiscoveredCamera, pluginId: str
    ) -> None:
        """Notify that a camera was discovered."""
        ...

    async def notifyCameraLost(self, cameraId: str, pluginId: str) -> None:
        """Notify that a camera was lost."""
        ...


@runtime_checkable
class DiscoveryManager(Protocol):
    """Discovery manager for camera discovery operations.

    Manages camera discovery providers from cameraController plugins.
    Accessed via `api.discoveryManager` in plugins.

    Example:
        ```python
        # Register a discovery provider (cameraController plugins only)
        provider = MyDiscoveryProvider()
        await api.discoveryManager.registerProvider(provider)

        # Start discovery
        await api.discoveryManager.startDiscovery()

        # Get discovered cameras
        cameras = await api.discoveryManager.getDiscoveredCameras()
        ```
    """

    async def registerProvider(self, provider: DiscoveryProvider) -> None:
        """
        Register a discovery provider (cameraController plugins only).

        Args:
            provider: The discovery provider implementation
        """
        ...

    async def unregisterProvider(self) -> None:
        """Unregister the discovery provider."""
        ...

    async def startDiscovery(self) -> None:
        """Start continuous discovery scanning."""
        ...

    async def stopDiscovery(self) -> None:
        """Stop discovery scanning."""
        ...

    async def rescan(self) -> None:
        """Trigger a manual rescan."""
        ...

    async def getDiscoveredCameras(self) -> list[DiscoveredCamera]:
        """
        Get all discovered cameras from this plugin.

        Returns:
            List of discovered cameras
        """
        ...
