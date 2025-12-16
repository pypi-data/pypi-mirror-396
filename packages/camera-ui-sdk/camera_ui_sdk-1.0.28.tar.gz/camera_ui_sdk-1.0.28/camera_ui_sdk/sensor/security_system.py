"""Security System sensor types and classes."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum, IntEnum
from typing import Any, Generic, Protocol, runtime_checkable

from typing_extensions import TypedDict, TypeVar

from .base import Sensor, SensorLike
from .types import SensorCategory, SensorType


class SecuritySystemState(IntEnum):
    """Security System state values (HomeKit compatible)."""

    StayArm = 0  # Home/Stay armed
    AwayArm = 1  # Away armed
    NightArm = 2  # Night armed
    Disarmed = 3  # Disarmed
    AlarmTriggered = 4  # Alarm triggered (CurrentState only)


class SecuritySystemProperty(str, Enum):
    """Security System property keys."""

    CurrentState = "currentState"  # Read-only (0-4)
    TargetState = "targetState"  # Read/Write (0-3)


class SecuritySystemProperties(TypedDict):
    """Security System properties interface."""

    currentState: int
    targetState: int


# Generic type for user-defined storage
TStorage = TypeVar("TStorage", bound=dict[str, Any], default=dict[str, Any])


@runtime_checkable
class SecuritySystemLike(SensorLike, Protocol):
    """Protocol for security system type checking."""

    @property
    def currentState(self) -> SecuritySystemState:
        """Current security system state (read-only)."""
        ...

    @property
    def targetState(self) -> SecuritySystemState:
        """Target security system state."""
        ...


class SecuritySystem(Sensor[SecuritySystemProperties, TStorage, str], Generic[TStorage]):
    """
    Security System Control.

    Bidirectional control for security/alarm systems.
    Compatible with HomeKit SecuritySystem service.

    Properties:
        currentState: Read-only, reflects actual system state (0-4)
        targetState: Read/write, what user wants (0-3, no ALARM_TRIGGERED)
    """

    _requires_frames = False

    def __init__(self, name: str = "Security System") -> None:
        super().__init__(name)

        # Initialize defaults - disarmed
        self.props.currentState = int(SecuritySystemState.Disarmed)
        self.props.targetState = int(SecuritySystemState.Disarmed)

    @property
    def type(self) -> SensorType:
        return SensorType.SecuritySystem

    @property
    def category(self) -> SensorCategory:
        return SensorCategory.Control

    @property
    def currentState(self) -> SecuritySystemState:
        """Current security system state (read-only from external perspective)."""
        value = self.props.currentState
        return SecuritySystemState(value) if value is not None else SecuritySystemState.Disarmed

    @currentState.setter
    def currentState(self, value: SecuritySystemState) -> None:
        """Set current state (for plugin use - e.g., when alarm is triggered)."""
        self.props.currentState = int(value)

    @property
    def targetState(self) -> SecuritySystemState:
        """Target security system state."""
        value = self.props.targetState
        return SecuritySystemState(value) if value is not None else SecuritySystemState.Disarmed

    @targetState.setter
    def targetState(self, value: SecuritySystemState) -> None:
        """Set target state (user request)."""
        # Target state cannot be ALARM_TRIGGERED
        if value == SecuritySystemState.AlarmTriggered:
            return
        self.props.targetState = int(value)

    # ========== Abstract Methods - Plugin Must Implement ==========

    @abstractmethod
    async def setTargetState(self, value: SecuritySystemState) -> None:
        """
        Set target state via hardware.

        Plugin must implement this to control the actual hardware.
        Update `self.targetState = value` and `self.currentState = value` after successful hardware call.

        Note: Target state cannot be AlarmTriggered - this method won't be called for that value.

        Args:
            value: The requested target state (0-3, not AlarmTriggered)

        Example:
            async def setTargetState(self, value: SecuritySystemState) -> None:
                await self.alarm_panel.arm(value)
                self.targetState = value
                self.currentState = value
        """
        ...

    async def setCurrentState(self, value: SecuritySystemState) -> None:
        """
        Set current state (for plugin use - e.g., when alarm is triggered).

        Default implementation just updates internal state.

        Args:
            value: The new current state
        """
        self.currentState = value
