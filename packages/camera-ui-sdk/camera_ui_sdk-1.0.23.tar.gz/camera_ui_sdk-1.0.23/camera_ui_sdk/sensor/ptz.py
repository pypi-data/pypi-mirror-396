"""PTZ control sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, Generic, Protocol, runtime_checkable

from typing_extensions import NotRequired, TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import PTZDirection, PTZPosition, SensorCategory, SensorType


class PTZCapability(str, Enum):
    """PTZ capabilities - describes what features this PTZ control supports."""

    Pan = "pan"
    Tilt = "tilt"
    Zoom = "zoom"
    Presets = "presets"
    Home = "home"


class PTZProperty(str, Enum):
    """PTZ control properties."""

    Position = "position"
    Moving = "moving"
    Presets = "presets"
    Velocity = "velocity"
    TargetPreset = "targetPreset"


class PTZControlProperties(TypedDict):
    """PTZ control properties interface."""

    position: PTZPosition
    moving: bool
    presets: list[str]
    velocity: NotRequired[PTZDirection | None]
    targetPreset: NotRequired[str | None]


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class PTZControlLike(SensorLike, Protocol):
    """Protocol for PTZ control type checking."""

    @property
    def position(self) -> PTZPosition:
        """Current PTZ position."""
        ...

    @property
    def moving(self) -> bool:
        """Whether PTZ is currently moving."""
        ...

    @property
    def presets(self) -> list[str]:
        """Available presets."""
        ...

    @property
    def velocity(self) -> PTZDirection | None:
        """Current velocity (for continuous move)."""
        ...

    @property
    def targetPreset(self) -> str | None:
        """Target preset to go to."""
        ...


class PTZControl(Sensor[PTZControlProperties, TStorage, PTZCapability], Generic[TStorage]):
    """
    PTZ Control.

    Bidirectional control for camera pan/tilt/zoom.

    Example:
        ```python
        # Move to absolute position
        ptz.position = {"pan": 45, "tilt": -10, "zoom": 0.5}

        # Continuous move
        ptz.continuousMove({"panSpeed": 1, "tiltSpeed": 0, "zoomSpeed": 0})

        # Stop all movement
        ptz.stop()

        # Go to preset
        ptz.goToPreset("Entrance")

        # Go to home position
        ptz.goHome()
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "PTZ") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.position = {"pan": 0, "tilt": 0, "zoom": 0}
        self.props.moving = False
        self.props.presets = []

    @property
    def type(self) -> SensorType:
        return SensorType.PTZ

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def position(self) -> PTZPosition:
        """Current PTZ position."""
        return self.props.position  # type: ignore[no-any-return]

    @position.setter
    def position(self, value: PTZPosition) -> None:
        self.props.position = value

    @property
    def moving(self) -> bool:
        """Whether PTZ is currently moving."""
        return self.props.moving  # type: ignore[no-any-return]

    @moving.setter
    def moving(self, value: bool) -> None:
        self.props.moving = value

    @property
    def presets(self) -> list[str]:
        """Available presets."""
        return self.props.presets  # type: ignore[no-any-return]

    @presets.setter
    def presets(self, value: list[str]) -> None:
        self.props.presets = value

    @property
    def velocity(self) -> PTZDirection | None:
        """Current velocity (for continuous move)."""
        return self.props.velocity  # type: ignore[no-any-return]

    @velocity.setter
    def velocity(self, value: PTZDirection | None) -> None:
        self.props.velocity = value

    @property
    def targetPreset(self) -> str | None:
        """Target preset to go to."""
        return self.props.targetPreset  # type: ignore[no-any-return]

    @targetPreset.setter
    def targetPreset(self, value: str | None) -> None:
        self.props.targetPreset = value

    # ========== Abstract Methods - Plugin Must Implement ==========

    @abstractmethod
    async def setPosition(self, value: PTZPosition) -> None:
        """
        Set PTZ position via hardware (absolute move).

        Plugin must implement this to control the actual hardware.
        Update `self.position = value` after successful hardware call.

        Args:
            value: Target position (pan, tilt, zoom)

        Example:
            async def setPosition(self, value: PTZPosition) -> None:
                await self.onvif_ptz.absolute_move(value)
                self.position = value
        """
        ...

    # ========== Optional Override Methods ==========

    async def setVelocity(self, value: PTZDirection | None) -> None:
        """
        Set PTZ velocity for continuous movement via RPC.

        Default implementation just sets the property.
        Override if hardware control is needed.

        Args:
            value: Movement velocity or None to stop
        """
        self.velocity = value

    async def setTargetPreset(self, value: str | None) -> None:
        """
        Set target preset via RPC.

        Default implementation just sets the property.
        Override if hardware control is needed.

        Args:
            value: Preset name or None
        """
        self.targetPreset = value

    async def goHome(self) -> None:
        """
        Go to home position via hardware.

        Optional - only implement if device supports home position.
        Default implementation sets position to { pan: 0, tilt: 0, zoom: 0 }.
        """
        await self.setPosition({"pan": 0, "tilt": 0, "zoom": 0})
