"""Doorbell trigger sensor types and classes."""

from __future__ import annotations

from enum import Enum
from typing import Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import SensorCategory, SensorType


class DoorbellProperty(str, Enum):
    """Doorbell trigger properties."""

    Ring = "ring"


class DoorbellTriggerProperties(TypedDict):
    """Doorbell trigger properties interface."""

    ring: bool


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class DoorbellTriggerLike(SensorLike, Protocol):
    """Protocol for doorbell trigger type checking."""

    @property
    def ring(self) -> bool:
        """Whether doorbell is currently ringing."""
        ...


class DoorbellTrigger(Sensor[DoorbellTriggerProperties, TStorage, str], Generic[TStorage]):
    """
    Doorbell Trigger.

    Event-based trigger for doorbell rings.
    Properties can be set directly: `doorbell.ring = True`

    Example:
        ```python
        class RingDoorbellTrigger(DoorbellTrigger):
            def __init__(self, ring_camera: RingCamera):
                super().__init__("Ring Doorbell")

                ring_camera.on_doorbell_pressed.subscribe(lambda:
                    setattr(self, 'ring', True)
                )
        ```
    """

    _requires_frames = False

    def __init__(self, name: str = "Doorbell") -> None:
        super().__init__(name)

        # Initialize defaults
        self.props.ring = False

    @property
    def type(self) -> SensorType:
        return SensorType.Doorbell

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Trigger

    @property
    def ring(self) -> bool:
        """Whether doorbell is currently ringing."""
        return self.props.ring  # type: ignore[no-any-return]

    @ring.setter
    def ring(self, value: bool) -> None:
        """Set ring state."""
        self.props.ring = value
