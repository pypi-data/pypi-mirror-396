"""Contact sensor types and classes."""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import SensorCategory, SensorType


class ContactProperty(str, Enum):
    """Contact sensor properties."""

    Detected = "detected"


class ContactSensorProperties(TypedDict):
    """Contact sensor properties interface."""

    detected: bool


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class ContactSensorLike(SensorLike, Protocol):
    """Protocol for contact sensor type checking."""

    @property
    def detected(self) -> bool:
        """Whether contact is detected (door/window open)."""
        ...


class ContactSensor(Sensor[ContactSensorProperties, TStorage, str], Generic[TStorage]):
    """
    Contact sensor for door/window open/closed detection.

    Properties can be set directly: `sensor.detected = True`

    Example:
        ```python
        class MyContactSensor(ContactSensor):
            def __init__(self, device: MyDevice):
                super().__init__("Door Contact")

                device.on_contact_changed.subscribe(lambda closed: setattr(self, "detected", closed))
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Contact Sensor") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.detected = False

    @property
    def type(self) -> SensorType:
        return SensorType.Contact

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Sensor

    @property
    def detected(self) -> bool:
        """Whether contact is detected (closed)."""
        return self.props.detected  # type: ignore[no-any-return]

    @detected.setter
    def detected(self, value: bool) -> None:
        """Set contact detected state."""
        self.props.detected = value
