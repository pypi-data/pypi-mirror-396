"""Light control sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import SensorCategory, SensorType


class LightCapability(str, Enum):
    """Light capabilities - describes what features this light supports."""

    Brightness = "brightness"


class LightProperty(str, Enum):
    """Light control properties."""

    On = "on"
    Brightness = "brightness"


class LightControlProperties(TypedDict):
    """Light control properties interface."""

    on: bool
    brightness: int


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class LightControlLike(SensorLike, Protocol):
    """Protocol for light control type checking."""

    @property
    def on(self) -> bool:
        """Whether light is on."""
        ...

    @property
    def brightness(self) -> int:
        """Brightness level (0-100)."""
        ...


class LightControl(Sensor[LightControlProperties, TStorage, LightCapability], Generic[TStorage]):
    """
    Light Control.

    Bidirectional control for camera spotlight/floodlight.
    Properties can be set directly: `light.on = True`

    Plugin must implement the abstract `setOn()` method for hardware control.
    The proxy handles change detection automatically to prevent infinite loops.

    Example:
        ```python
        class RingLightControl(LightControl):
            def __init__(self, ring_camera: RingCamera):
                super().__init__("Ring Light")
                self.ring_camera = ring_camera

                # Subscribe to hardware events in constructor
                ring_camera.on_data.subscribe(lambda data:
                    setattr(self, 'on', data.led_status == 'on') if data.led_status else None
                )

            async def setOn(self, value: bool) -> None:
                await self.ring_camera.set_light(value)
                self.on = value
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Light") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.on = False
        self.props.brightness = 100

    @property
    def type(self) -> SensorType:
        return SensorType.Light

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def on(self) -> bool:
        """Whether light is on."""
        return self.props.on  # type: ignore[no-any-return]

    @on.setter
    def on(self, value: bool) -> None:
        """Set light on state. Proxy handles change detection."""
        self.props.on = value

    @property
    def brightness(self) -> int:
        """Brightness level (0-100)."""
        return self.props.brightness  # type: ignore[no-any-return]

    @brightness.setter
    def brightness(self, value: int) -> None:
        """Set brightness level. Proxy handles change detection."""
        self.props.brightness = max(0, min(100, value))

    # ========== Abstract Methods - Plugin MUST Implement ==========

    @abstractmethod
    async def setOn(self, value: bool) -> None:
        """
        Set light on/off state via hardware.

        Plugin must implement this to control the actual hardware.
        Update `self.on = value` after successful hardware call.

        Args:
            value: Whether to turn the light on

        Example:
            async def setOn(self, value: bool) -> None:
                try:
                    await self.ring_camera.set_light(value)
                    self.on = value
                except Exception:
                    pass  # Error - don't update state
        """
        ...

    # ========== Optional Override Methods ==========

    async def setBrightness(self, value: int) -> None:
        """
        Set light brightness level.

        Default implementation just sets the property.
        Override if hardware control is needed.

        Args:
            value: Brightness level (0-100)
        """
        self.brightness = value
