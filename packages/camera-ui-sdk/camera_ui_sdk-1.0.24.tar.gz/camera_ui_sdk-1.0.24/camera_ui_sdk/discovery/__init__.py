"""Discovery module exports."""

from .provider import BaseDiscoveryProvider, DiscoveryProvider
from .types import (
    DiscoveredCamera,
    DiscoveryCamerasEvent,
    DiscoveryConnectedEvent,
    DiscoveryErrorEvent,
    DiscoveryProviderInfo,
    DiscoveryStartedEvent,
    DiscoveryStatus,
    DiscoveryStoppedEvent,
)

__all__ = [
    # Types
    "DiscoveredCamera",
    "DiscoveryStatus",
    "DiscoveryProviderInfo",
    # Event types
    "DiscoveryCamerasEvent",
    "DiscoveryStartedEvent",
    "DiscoveryStoppedEvent",
    "DiscoveryErrorEvent",
    "DiscoveryConnectedEvent",
    # Provider
    "DiscoveryProvider",
    "BaseDiscoveryProvider",
]
