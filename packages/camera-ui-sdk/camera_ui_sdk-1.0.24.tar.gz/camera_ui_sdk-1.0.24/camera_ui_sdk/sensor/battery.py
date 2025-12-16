"""Battery info sensor types and classes."""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import ChargingState, SensorCategory, SensorType


class BatteryCapability(str, Enum):
    """Battery capabilities - describes what features this battery sensor supports."""

    LowBattery = "lowBattery"
    Charging = "charging"


class BatteryProperty(str, Enum):
    """Battery info properties."""

    Level = "level"
    Charging = "charging"
    Low = "low"


class BatteryInfoProperties(TypedDict):
    """Battery info properties interface."""

    level: int
    charging: ChargingState
    low: bool


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class BatteryInfoLike(SensorLike, Protocol):
    """Protocol for battery info type checking."""

    @property
    def level(self) -> int:
        """Battery level (0-100)."""
        ...

    @property
    def charging(self) -> ChargingState:
        """Charging state."""
        ...

    @property
    def low(self) -> bool:
        """Whether battery is low."""
        ...


class BatteryInfo(Sensor[BatteryInfoProperties, TStorage, BatteryCapability], Generic[TStorage]):
    """
    Battery Info.

    Read-only hardware status for battery-powered cameras.
    Properties can be set directly: `battery.level = 85`

    Example:
        ```python
        class RingBatteryInfo(BatteryInfo):
            def __init__(self, ring_camera: RingCamera):
                super().__init__("Ring Battery")
                self.capabilities = [BatteryCapability.Charging, BatteryCapability.LowBattery]

                ring_camera.on_battery_level.subscribe(lambda:
                    self.update_from_ring_camera(ring_camera)
                )

            def update_from_ring_camera(self, ring_camera: RingCamera) -> None:
                self.level = ring_camera.battery_level or 100
                self.charging = ChargingState.Charging if ring_camera.is_charging else ChargingState.NotCharging
                self.low = ring_camera.has_low_battery
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Battery") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.level = 100
        self.props.charging = ChargingState.NotCharging
        self.props.low = False

    @property
    def type(self) -> SensorType:
        return SensorType.Battery

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Info

    @property
    def level(self) -> int:
        """Battery level (0-100)."""
        return self.props.level  # type: ignore[no-any-return]

    @level.setter
    def level(self, value: int) -> None:
        """Set battery level (clamped to 0-100)."""
        self.props.level = max(0, min(100, value))

    @property
    def charging(self) -> ChargingState:
        """Charging state."""
        return self.props.charging  # type: ignore[no-any-return]

    @charging.setter
    def charging(self, value: ChargingState) -> None:
        """Set charging state."""
        self.props.charging = value

    @property
    def low(self) -> bool:
        """Whether battery is low."""
        return self.props.low  # type: ignore[no-any-return]

    @low.setter
    def low(self, value: bool) -> None:
        """Set low battery state."""
        self.props.low = value
