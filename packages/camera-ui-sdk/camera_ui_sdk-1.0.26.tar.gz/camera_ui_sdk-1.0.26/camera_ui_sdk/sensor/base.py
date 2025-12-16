"""Base sensor classes and protocols."""

from __future__ import annotations

import asyncio
import contextlib
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, runtime_checkable
from uuid import uuid4

from ..utils import is_equal
from .types import PropertyChangedEvent, SensorCategory, SensorType

if TYPE_CHECKING:
    from ..storage.schema import JsonSchema
    from ..storage.storages import DeviceStorage

# Type alias for property change listeners
PropertyChangeListener = Callable[[PropertyChangedEvent], None]
"""Callback type for detailed property change events."""

# Type variables for Sensor generics
# Using Mapping as bound allows TypedDict to be used as TProperties
TProperties = TypeVar("TProperties", bound=Mapping[str, Any])
TStorage = TypeVar("TStorage", bound=dict[str, Any])
TCapability = TypeVar("TCapability", bound=str)


class PropertiesProxy(Generic[TProperties]):
    """
    Proxy class that intercepts property writes and triggers RPC updates.

    Similar to JavaScript's Proxy, this class intercepts attribute access
    and calls the update function when properties are changed.

    Note: For type-safe property access in sensor subclasses, use typed
    property getters that access _properties_store directly with appropriate
    return type annotations.
    """

    _store: dict[str, Any]
    _on_change: Callable[[str, Any, Any], None]

    def __init__(
        self,
        store: dict[str, Any],
        on_change: Callable[[str, Any, Any], None],
    ) -> None:
        """
        Initialize the properties proxy.

        Args:
            store: The underlying properties storage dict
            on_change: Callback called with (key, new_value, old_value) on changes
        """
        object.__setattr__(self, "_store", store)
        object.__setattr__(self, "_on_change", on_change)

    def __getattr__(self, key: str) -> Any:
        """Get a property value."""
        store: dict[str, Any] = object.__getattribute__(self, "_store")
        if key.startswith("_"):
            return object.__getattribute__(self, key)
        return store.get(key)

    def __setattr__(self, key: str, value: Any) -> None:
        """Set a property value and trigger update callback."""
        if key.startswith("_"):
            object.__setattr__(self, key, value)
            return

        store: dict[str, Any] = object.__getattribute__(self, "_store")
        on_change: Callable[[str, Any, Any], None] = object.__getattribute__(self, "_on_change")

        old_value = store.get(key)
        # Deep compare for objects/arrays
        if not is_equal(old_value, value, True):
            store[key] = value
            on_change(key, value, old_value)

    def __getitem__(self, key: str) -> Any:
        """Get a property value via dict-like access."""
        store: dict[str, Any] = object.__getattribute__(self, "_store")
        return store.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a property value via dict-like access."""
        self.__setattr__(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a property value with optional default."""
        store: dict[str, Any] = object.__getattribute__(self, "_store")
        return store.get(key, default)


@runtime_checkable
class SensorLike(Protocol):
    """
    SensorLike interface - common interface for Sensor and SensorProxy.

    This allows plugins to access sensors (both owned and from other plugins)
    through a unified interface.

    Use type guards (isMotionSensor, isLightControl, etc.) for runtime type checking.
    """

    # Properties (camelCase for RPC compatibility)
    @property
    def id(self) -> str:
        """Unique sensor ID."""
        ...

    @property
    def type(self) -> SensorType:
        """Sensor type."""
        ...

    @property
    def name(self) -> str:
        """Stable name (set by plugin, used for storage key)."""
        ...

    @property
    def displayName(self) -> str:
        """Display name for UI/HomeKit (initially = name, can be changed by user)."""
        ...

    @property
    def pluginId(self) -> str | None:
        """Plugin ID that provides this sensor."""
        ...

    @property
    def capabilities(self) -> list[str]:
        """Sensor capabilities (e.g., PTZCapability.Pan, LightCapability.Brightness)."""
        ...

    # Methods (camelCase for RPC compatibility)
    def getPropertyValue(self, property: str) -> Any | None:
        """
        Get a property value.

        Args:
            property: The property key (use enum values like MotionProperty.Detected)

        Returns:
            The property value or None
        """
        ...

    def getAllPropertyValues(self) -> dict[str, Any]:
        """
        Get all property values.

        Returns:
            All properties as a dictionary
        """
        ...

    async def setPropertyValue(self, property: str, value: Any) -> None:
        """
        Set a property value (for Control sensors).
        Note: Only works for Control sensors, others are read-only.

        Args:
            property: The property key (use enum values like LightProperty.On)
            value: The new value
        """
        ...

    def onPropertyChanged(self, callback: Callable[[str, Any], None]) -> Callable[[], None]:
        """
        Subscribe to property changes for this sensor.

        Args:
            callback: Callback with property key and new value

        Returns:
            Unsubscribe function
        """
        ...

    def onPropertyChangedDetailed(self, callback: PropertyChangeListener) -> Callable[[], None]:
        """
        Subscribe to detailed property changes with full event info.

        Args:
            callback: Callback receiving PropertyChangedEvent

        Returns:
            Unsubscribe function
        """
        ...

    def onCapabilitiesChanged(self, callback: Callable[[list[str]], None]) -> Callable[[], None]:
        """
        Subscribe to capability changes for this sensor.

        Args:
            callback: Callback with new capabilities array

        Returns:
            Unsubscribe function
        """
        ...

    def hasCapability(self, capability: str) -> bool:
        """
        Check if sensor has a specific capability.

        Args:
            capability: The capability to check (use enum values like PTZCapability.Zoom)

        Returns:
            True if the sensor has the capability
        """
        ...


class Sensor(ABC, Generic[TProperties, TStorage, TCapability]):
    """
    Abstract Base Class for all sensors.

    Plugins extend this class to implement custom sensor functionality.
    The sensor communicates with the server via RPC.

    Properties are intercepted via PropertiesProxy and automatically synchronized via RPC.
    Plugin developers can use `self.props.detected = True` and the update
    is automatically propagated.

    Type Parameters:
        TProperties: Type of the sensor properties dictionary
        TStorage: Type of the sensor storage dictionary
        TCapability: Type of the sensor capabilities (enum)
    """

    # Class-level flag for detector sensors
    _requires_frames: bool = False

    def __init__(self, name: str) -> None:
        """
        Create a new sensor instance.

        Args:
            name: Stable name for the sensor (used as storage key)
        """
        self._camera_id: str | None = None
        self._name = name
        self._id = str(uuid4())
        self._display_name = name
        self._plugin_id: str | None = None
        self._capabilities: list[TCapability] = []
        self._property_listeners: list[Callable[[str, Any], None]] = []
        self._detailed_listeners: set[PropertyChangeListener] = set()
        self._capabilities_listeners: list[Callable[[list[str]], None]] = []
        self._assignment_listeners: list[Callable[[bool], None]] = []
        self._update_fn: Callable[[str, Any], None] | None = None
        self._capabilities_change_fn: Callable[[list[str]], None] | None = None
        self._restart_fn: Callable[[], Any] | None = None
        self._storage: DeviceStorage | None = None
        self._is_assigned: bool = False

        # Properties storage and proxy (like TypeScript's _propertiesStore and _propertiesProxy)
        self._properties_store: dict[str, Any] = {}
        self._properties_proxy: PropertiesProxy[TProperties] = PropertiesProxy(
            self._properties_store,
            self._on_property_change,
        )

    @property
    @abstractmethod
    def type(self) -> SensorType:
        """Sensor type - must be implemented by subclasses."""
        ...

    @property
    @abstractmethod
    def category(self) -> SensorCategory:
        """Sensor category - must be implemented by subclasses."""
        ...

    @property
    def id(self) -> str:
        """Unique sensor ID."""
        return self._id

    @property
    def name(self) -> str:
        """Stable name (set by plugin, used for storage key)."""
        return self._name

    @property
    def displayName(self) -> str:
        """Display name for UI/HomeKit."""
        return self._display_name

    @displayName.setter
    def displayName(self, value: str) -> None:
        self._display_name = value

    @property
    def pluginId(self) -> str | None:
        """Plugin ID that provides this sensor."""
        return self._plugin_id

    @property
    def cameraId(self) -> str | None:
        """Camera ID this sensor is associated with."""
        return self._camera_id

    @property
    def capabilities(self) -> list[TCapability]:
        """Sensor capabilities."""
        return self._capabilities.copy()

    @capabilities.setter
    def capabilities(self, value: list[TCapability]) -> None:
        """
        Set sensor capabilities.

        Updates the capabilities and broadcasts to consumers via RPC.
        Capabilities are automatically deduplicated.

        Args:
            value: The new capabilities array
        """
        # Deduplicate capabilities
        self._capabilities = list(dict.fromkeys(value))
        # Broadcast to SensorController (for RPC propagation)
        caps_list: list[str] = [str(c) for c in self._capabilities]
        if self._capabilities_change_fn:
            self._capabilities_change_fn(caps_list)
        # Notify local listeners
        for listener in self._capabilities_listeners:
            with contextlib.suppress(Exception):
                listener(caps_list)

    @property
    def requiresFrames(self) -> bool:
        """Whether this sensor requires video/audio frames for detection."""
        return self._requires_frames

    @property
    def schema(self) -> list[JsonSchema]:
        """
        Configuration schemas for this sensor.

        Override in subclass to provide sensor-specific configuration options.
        Returns empty list by default (no configuration).
        """
        return []

    @property
    def storage(self) -> DeviceStorage | None:
        """
        Sensor storage instance.

        Set by the runtime when the sensor is registered with schemas.
        """
        return self._storage

    @property
    def isAssigned(self) -> bool:
        """Whether this sensor is assigned (active) for the camera."""
        return self._is_assigned

    @property
    def props(self) -> PropertiesProxy[TProperties]:
        """
        Access to proxied properties for derived classes.

        Writes to this proxy trigger RPC updates automatically.
        Use like: `self.props.detected = True`
        """
        return self._properties_proxy

    @property
    def rawProps(self) -> dict[str, Any]:
        """
        Read-only access to raw properties (no proxy).

        Use this for reading property values without triggering updates.
        """
        return self._properties_store

    def _notify_metadata_update(self, property: str, value: Any) -> None:
        """
        Notify the backend of a metadata property change (e.g., modelSpec).

        Use this for properties that are not part of the sensor's TProperties interface.

        Args:
            property: The property name
            value: The new property value
        """
        if self._update_fn:
            self._update_fn(property, value)

    def _on_property_change(self, key: str, value: Any, old_value: Any) -> None:
        """
        Internal callback when a property changes via the proxy.

        Args:
            key: Property key
            value: New value
            old_value: Previous value
        """
        # Fire-and-forget RPC update
        if self._update_fn:
            self._update_fn(key, value)

        # Notify local listeners
        self._notifyListeners(key, value, old_value)

    def _setStorage(self, storage: DeviceStorage) -> None:
        """
        Set storage instance (called by runtime).

        Args:
            storage: The DeviceStorage instance for this sensor
        """
        self._storage = storage

    def _setAssigned(self, assigned: bool) -> None:
        """
        Set assignment status (called by runtime).

        Args:
            assigned: Whether this sensor is assigned to the camera
        """
        if self._is_assigned != assigned:
            self._is_assigned = assigned
            for listener in self._assignment_listeners:
                listener(assigned)

    def onAssignmentChanged(self, callback: Callable[[bool], None]) -> Callable[[], None]:
        """
        Subscribe to assignment changes.

        Args:
            callback: Callback receiving the new assignment status

        Returns:
            Unsubscribe function
        """
        self._assignment_listeners.append(callback)
        return lambda: self._assignment_listeners.remove(callback)

    def toJSON(self) -> dict[str, Any]:
        """
        Serialize sensor to JSON for registration.

        Returns:
            Dictionary representation of the sensor for RPC registration
        """
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "displayName": self.displayName,
            "category": self.category,
            "properties": self._getProperties(),
            "capabilities": [str(c) for c in self.capabilities],
        }

    def _setPropertyInternal(self, key: str, value: Any) -> None:
        """
        Set property from external source (no RPC callback).

        Only notifies listeners if value actually changed to avoid feedback loops.
        This bypasses the proxy to avoid re-broadcasting.

        Args:
            key: Property key
            value: Property value
        """
        old_value = self._properties_store.get(key)
        if old_value != value:
            self._properties_store[key] = value
            self._notifyListeners(key, value, old_value)

    def _onBackendPropertyChanged(self, property: str, value: Any) -> None:
        """
        Handle backend-initiated property change.

        Called by the runtime when backend changes a property
        (e.g., motion dwell timer reset).

        Args:
            property: The property that changed
            value: The new value
        """
        self._setPropertyInternal(property, value)

    # RPC-exposed methods (camelCase for compatibility)

    def getPropertyValue(self, property: str) -> Any | None:
        """Get a property value."""
        return self._properties_store.get(property)

    def getAllPropertyValues(self) -> dict[str, Any]:
        """Get all property values."""
        return self._properties_store.copy()

    async def setPropertyValue(self, property: str, value: Any) -> None:
        """
        Set a property value (SensorLike interface).

        Routes to setX() methods if they exist, otherwise sets directly on proxy.

        Args:
            property: The property name
            value: The new property value
        """
        # Route to setX() method if it exists (e.g., setActive, setOn, setDetected)
        method_name = f"set{property[0].upper()}{property[1:]}"
        method = getattr(self, method_name, None)

        if callable(method):
            result = method(value)
            # Await if it's a coroutine (for async control sensor hooks)
            if asyncio.iscoroutine(result):
                await result
        else:
            # Fallback: set directly on proxy (with value-change check)
            if self._properties_store.get(property) != value:
                setattr(self._properties_proxy, property, value)

    def hasCapability(self, capability: TCapability | str) -> bool:
        """Check if sensor has a specific capability."""
        return capability in self._capabilities

    def onPropertyChanged(self, callback: Callable[[str, Any], None]) -> Callable[[], None]:
        """Subscribe to property changes."""
        self._property_listeners.append(callback)
        return lambda: self._property_listeners.remove(callback)

    def onPropertyChangedDetailed(self, callback: PropertyChangeListener) -> Callable[[], None]:
        """
        Subscribe to detailed property changes with full event info.

        This provides more context than onPropertyChanged(), including:
        - cameraId, sensorId, sensorType
        - previousValue
        - timestamp

        Args:
            callback: Callback receiving PropertyChangedEvent

        Returns:
            Unsubscribe function
        """
        self._detailed_listeners.add(callback)
        return lambda: self._detailed_listeners.discard(callback)

    def _notifyListeners(self, property: str, value: Any, previousValue: Any) -> None:
        """
        Notify all listeners of a property change.

        Args:
            property: Property key
            value: New value
            previousValue: Previous value
        """
        # Skip notification if sensor not yet attached to camera
        if not self._camera_id:
            return

        # Notify detailed listeners with full event
        if self._detailed_listeners:
            event: PropertyChangedEvent = {
                "cameraId": self._camera_id,
                "sensorId": self._id,
                "sensorType": self.type,
                "property": property,
                "value": value,
                "previousValue": previousValue,
                "timestamp": int(time.time() * 1000),
            }
            for detailed_listener in self._detailed_listeners:
                with contextlib.suppress(Exception):
                    detailed_listener(event)
        # Notify simple listeners
        for simple_listener in self._property_listeners:
            with contextlib.suppress(Exception):
                simple_listener(property, value)

    def onCapabilitiesChanged(self, callback: Callable[[list[str]], None]) -> Callable[[], None]:
        """Subscribe to capability changes."""
        self._capabilities_listeners.append(callback)
        return lambda: self._capabilities_listeners.remove(callback)

    def _setCameraId(self, camera_id: str) -> None:
        """
        Set camera ID (called by runtime).

        Args:
            camera_id: ID of the camera this sensor is for
        """
        self._camera_id = camera_id

    def _setPluginId(self, plugin_id: str) -> None:
        """
        Set plugin ID (called by runtime).

        Args:
            plugin_id: ID of the plugin that provides this sensor
        """
        self._plugin_id = plugin_id

    def _init(
        self,
        update_fn: Callable[[str, Any], None],
        capabilities_change_fn: Callable[[list[str]], None],
    ) -> None:
        """
        Internal initialization - sets up the RPC callbacks.

        Called by the runtime when the sensor is registered.

        Args:
            update_fn: Callback to notify server of property changes
            capabilities_change_fn: Callback to notify server of capability changes
        """
        self._update_fn = update_fn
        self._capabilities_change_fn = capabilities_change_fn

    def _initRestartFn(self, restart_fn: Callable[[], Any]) -> None:
        """
        Initialize restart function (called by backend).

        Args:
            restart_fn: Function to call when sensor needs restart
        """
        self._restart_fn = restart_fn

    async def requestRestart(self) -> None:
        """
        Request sensor restart from backend.

        Use this after changing internal state that affects modelSpec.
        Backend will unregister + register with fresh modelSpec values.

        Example:
            ```python
            class MyObjectSensor(ObjectDetectorSensor):
                def __init__(self):
                    super().__init__("My Object")
                    self._current_model = "yolov9m_320"

                @property
                def modelSpec(self) -> ModelSpec:
                    size = 320 if "320" in self._current_model else 640
                    return {
                        "input": {"width": size, "height": size, "format": "rgb"},
                        "outputLabels": COCO_80_LABELS,
                    }

                async def switch_model(self, new_model: str) -> None:
                    self._current_model = new_model
                    await self.requestRestart()  # Backend handles unregister/register
            ```
        """
        if self._restart_fn:
            result = self._restart_fn()
            if asyncio.iscoroutine(result):
                await result

    def _cleanup(self) -> None:
        """Internal cleanup - called when sensor is unregistered."""
        self._update_fn = None
        self._capabilities_change_fn = None
        self._restart_fn = None
        self._storage = None
        self._is_assigned = False
        self._assignment_listeners.clear()
        self._detailed_listeners.clear()
        self._property_listeners.clear()
        self._capabilities_listeners.clear()

    def _getProperties(self) -> dict[str, Any]:
        """Get all properties (internal use)."""
        return self._properties_store.copy()
