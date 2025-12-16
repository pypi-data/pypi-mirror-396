"""Siren control sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import SensorCategory, SensorType


class SirenCapability(str, Enum):
    """Siren capabilities - describes what features this siren supports."""

    Volume = "volume"


class SirenProperty(str, Enum):
    """Siren control properties."""

    Active = "active"
    Volume = "volume"


class SirenControlProperties(TypedDict):
    """Siren control properties interface."""

    active: bool
    volume: int


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class SirenControlLike(SensorLike, Protocol):
    """Protocol for siren control type checking."""

    @property
    def active(self) -> bool:
        """Whether siren is active."""
        ...

    @property
    def volume(self) -> int:
        """Volume level (0-100)."""
        ...


class SirenControl(Sensor[SirenControlProperties, TStorage, SirenCapability], Generic[TStorage]):
    """
    Siren Control.

    Bidirectional control for camera siren/alarm.
    Properties can be set directly: `siren.active = True`

    Plugin must implement the abstract `setActive()` method for hardware control.
    The proxy handles change detection automatically to prevent infinite loops.

    Example:
        ```python
        class RingSirenControl(SirenControl):
            def __init__(self, ring_camera: RingCamera):
                super().__init__("Ring Siren")
                self.ring_camera = ring_camera

                # Subscribe to hardware events in constructor
                ring_camera.on_data.subscribe(lambda data:
                    setattr(self, 'active', data.siren_status.seconds_remaining > 0)
                    if data.siren_status else None
                )

            async def setActive(self, value: bool) -> None:
                await self.ring_camera.set_siren(value)
                self.active = value
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Siren") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.active = False
        self.props.volume = 100

    @property
    def type(self) -> SensorType:
        return SensorType.Siren

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def active(self) -> bool:
        """Whether siren is active."""
        return self.props.active  # type: ignore[no-any-return]

    @active.setter
    def active(self, value: bool) -> None:
        """Set siren active state. Proxy handles change detection."""
        self.props.active = value

    @property
    def volume(self) -> int:
        """Volume level (0-100)."""
        return self.props.volume  # type: ignore[no-any-return]

    @volume.setter
    def volume(self, value: int) -> None:
        """Set volume level. Proxy handles change detection."""
        self.props.volume = max(0, min(100, value))

    # ========== Abstract Methods - Plugin MUST Implement ==========

    @abstractmethod
    async def setActive(self, value: bool) -> None:
        """
        Set siren active state via hardware.

        Plugin must implement this to control the actual hardware.
        Update `self.active = value` after successful hardware call.

        Args:
            value: Whether to activate the siren

        Example:
            async def setActive(self, value: bool) -> None:
                try:
                    await self.ring_camera.set_siren(value)
                    self.active = value
                except Exception:
                    pass  # Error - don't update state
        """
        ...

    # ========== Optional Override Methods ==========

    async def setVolume(self, value: int) -> None:
        """
        Set siren volume level.

        Default implementation just sets the property.
        Override if hardware control is needed.

        Args:
            value: Volume level (0-100)
        """
        self.volume = value
