"""Discovery types and interfaces."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict


class DiscoveryStatus(str, Enum):
    """Discovery provider status."""

    Idle = "idle"
    Scanning = "scanning"
    Stopped = "stopped"
    Error = "error"


class DiscoveredCamera(TypedDict, total=False):
    """Discovered camera from network scan."""

    # Required fields
    id: str
    """Unique discovery ID (plugin-generated, stable across rescans)."""
    name: str
    """Camera name (from device or auto-generated)."""
    address: str
    """IP address or hostname."""
    discoveredAt: int
    """Discovery timestamp."""

    # Optional fields
    port: int
    """Port number."""
    manufacturer: str
    """Manufacturer name."""
    model: str
    """Model name."""
    serialNumber: str
    """Serial number (for deduplication)."""
    macAddress: str
    """MAC address."""
    thumbnailUrl: str
    """Thumbnail/snapshot URL (optional preview)."""
    protocols: list[str]
    """Supported protocols (e.g., ['rtsp', 'onvif', 'http'])."""
    metadata: dict[str, object]
    """Plugin-specific metadata."""


class DiscoveryProviderInfo(TypedDict, total=False):
    """Discovery provider info (for UI display)."""

    pluginId: str
    """Plugin ID."""
    name: str
    """Provider display name."""
    description: str
    """Provider description."""
    status: DiscoveryStatus
    """Current status."""
    cameraCount: int
    """Number of cameras found."""
    lastScanAt: int
    """Last scan timestamp."""
    error: str
    """Error message (if status is Error)."""


class DiscoveryCamerasEvent(TypedDict):
    """Event data for discovery:cameras event."""

    pluginId: str
    cameras: list[DiscoveredCamera]


class DiscoveryStartedEvent(TypedDict):
    """Event data for discovery:started event."""

    pluginId: str


class DiscoveryStoppedEvent(TypedDict):
    """Event data for discovery:stopped event."""

    pluginId: str
    total: int


class DiscoveryErrorEvent(TypedDict):
    """Event data for discovery:error event."""

    pluginId: str
    error: str


class DiscoveryConnectedEvent(TypedDict):
    """Event data for discovery:connected event."""

    pluginId: str
    discoveredId: str
    cameraId: str
