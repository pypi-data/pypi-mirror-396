"""Switch control sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import SensorCategory, SensorType


class SwitchProperty(str, Enum):
    """Switch control properties."""

    On = "on"


class SwitchControlProperties(TypedDict):
    """Switch control properties interface."""

    on: bool


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class SwitchControlLike(SensorLike, Protocol):
    """Protocol for switch control type checking."""

    @property
    def on(self) -> bool:
        """Whether switch is on."""
        ...


class SwitchControl(Sensor[SwitchControlProperties, TStorage, str], Generic[TStorage]):
    """
    Switch Control.

    Simple on/off control for smart plugs, relays, and generic switches.
    Properties can be set directly: `switch.on = True`

    Plugin must implement the abstract `setOn()` method for hardware control.
    The proxy handles change detection automatically to prevent infinite loops.

    Example:
        ```python
        class MySwitchControl(SwitchControl):
            def __init__(self, device: MyDevice):
                super().__init__("My Switch")
                self.device = device

                # Subscribe to hardware events in constructor
                device.on_state_change.subscribe(lambda state:
                    setattr(self, 'on', state == 'on')
                )

            async def setOn(self, value: bool) -> None:
                await self.device.set_power(value)
                self.on = value
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Switch") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.on = False

    @property
    def type(self) -> SensorType:
        return SensorType.Switch

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def on(self) -> bool:
        """Whether switch is on."""
        return self.props.on  # type: ignore[no-any-return]

    @on.setter
    def on(self, value: bool) -> None:
        """Set switch on state. Proxy handles change detection."""
        self.props.on = value

    # ========== Abstract Methods - Plugin MUST Implement ==========

    @abstractmethod
    async def setOn(self, value: bool) -> None:
        """
        Set switch on/off state via hardware.

        Plugin must implement this to control the actual hardware.
        Update `self.on = value` after successful hardware call.

        Args:
            value: Whether to turn the switch on

        Example:
            async def setOn(self, value: bool) -> None:
                try:
                    await self.device.set_power(value)
                    self.on = value
                except Exception:
                    pass  # Error - don't update state
        """
        ...
