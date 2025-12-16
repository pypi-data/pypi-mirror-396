"""Camera configuration types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypedDict, runtime_checkable

from .streaming import StreamUrls
from .types import (
    CameraAspectRatio,
    CameraRole,
    StreamingRole,
    VideoStreamingMode,
)

if TYPE_CHECKING:
    from .streaming import ProbeConfig, ProbeStream


class CameraInformation(TypedDict, total=False):
    """Camera information metadata."""

    model: str
    manufacturer: str
    hardware: str
    serialNumber: str
    firmwareVersion: str
    supportUrl: str


class CameraFrameWorkerSettings(TypedDict):
    """Frame worker settings for a camera."""

    fps: int


class CameraInput(TypedDict):
    """Camera input source configuration."""

    _id: str
    name: str
    role: CameraRole
    useForSnapshot: bool
    hotMode: bool
    preload: bool
    prebuffer: bool
    urls: StreamUrls


class CameraInputSettings(TypedDict):
    """Camera input settings."""

    _id: str
    name: str
    role: CameraRole
    useForSnapshot: bool
    hotMode: bool
    preload: bool
    prebuffer: bool
    urls: list[str]


class CameraConfigInputSettings(TypedDict):
    """Camera config input settings (without _id and urls)."""

    name: str
    role: CameraRole
    useForSnapshot: bool
    hotMode: bool
    preload: bool
    prebuffer: bool


class BaseCameraConfig(TypedDict, total=False):
    """Base camera configuration."""

    name: str
    nativeId: str
    isCloud: bool
    disabled: bool
    info: CameraInformation


class CameraConfig(BaseCameraConfig):
    """Full camera configuration with sources."""

    sources: list[CameraConfigInputSettings]


class CameraUiSettings(TypedDict):
    """Camera UI display settings."""

    streamingMode: VideoStreamingMode
    streamingSource: StreamingRole | str  # 'auto' or a StreamingRole
    aspectRatio: CameraAspectRatio


class CameraRecordingSettings(TypedDict):
    """Camera recording settings."""

    enabled: bool


class CameraSourceData(CameraConfigInputSettings):
    """Raw camera source data from server."""

    _id: str
    urls: StreamUrls


@runtime_checkable
class CameraSource(Protocol):
    """Camera source interface with snapshot capability."""

    _id: str
    name: str
    role: CameraRole
    useForSnapshot: bool
    hotMode: bool
    preload: bool
    prebuffer: bool
    urls: StreamUrls

    async def snapshot(self, forceNew: bool = False) -> bytes | None:
        """Take a snapshot from this source.

        Args:
            forceNew: Whether to force a new snapshot instead of using a cached one.
        Returns:
            The snapshot image data as bytes, or None if snapshot failed.

        """
        ...

    async def probeStream(
        self, probeConfig: ProbeConfig | None = None, refresh: bool = False
    ) -> ProbeStream | None:
        """Probe the stream to get information about it.

        Args:
            probeConfig: Optional configuration for probing.
            refresh: Whether to refresh the probe data.
        Returns:
            The probed stream information, or None if probing failed.

        """
        ...
