"""Storage interfaces for plugins."""

from __future__ import annotations

from typing import Any, Generic, Protocol, overload, runtime_checkable

from typing_extensions import TypeVar

from .schema import FormSubmitResponse, JsonSchema, SchemaConfig

# TypeVar for generic getValue - matches TypeScript's U in overloads
# Using typing_extensions for default parameter support in Python < 3.13
V1 = TypeVar("V1", default=str)
V2 = TypeVar("V2", default=dict[str, Any])


@runtime_checkable
class DeviceStorage(Protocol, Generic[V2]):
    """Device storage for plugin configuration."""

    schemas: list[JsonSchema]
    values: V2

    @overload
    async def getValue(self, key: str) -> V1 | None: ...
    @overload
    async def getValue(self, key: str, default_value: V1) -> V1: ...
    async def getValue(self, key: str, default_value: V1 | None = None) -> V1 | None:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default_value: Default value if key doesn't exist

        Returns:
            The configuration value or default
        """
        ...

    async def setValue(self, key: str, new_value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            new_value: New value to set
        """
        ...

    async def submitValue(self, key: str, new_value: Any) -> FormSubmitResponse | None:
        """
        Submit a value (for button/submit schemas).

        Args:
            key: Schema key
            new_value: Value to submit

        Returns:
            Optional response with toast message or new schema
        """
        ...

    def hasValue(self, key: str) -> bool:
        """
        Check if a value exists.

        Args:
            key: Configuration key

        Returns:
            True if the value exists
        """
        ...

    async def getConfig(self) -> SchemaConfig:
        """
        Get the full configuration.

        Returns:
            Schema configuration with schemas and values
        """
        ...

    async def setConfig(self, new_config: V2) -> None:
        """
        Set the full configuration.

        Args:
            new_config: New configuration values
        """
        ...

    async def addSchema(self, schema: JsonSchema) -> None:
        """
        Add a new schema.

        Args:
            schema: Schema to add
        """
        ...

    def removeSchema(self, key: str) -> None:
        """
        Remove a schema.

        Args:
            key: Schema key to remove
        """
        ...

    async def changeSchema(self, key: str, new_schema: dict[str, Any]) -> None:
        """
        Update a schema.

        Args:
            key: Schema key to update
            new_schema: Partial schema with updates
        """
        ...

    def getSchema(self, key: str) -> JsonSchema | None:
        """
        Get a schema by key.

        Args:
            key: Schema key

        Returns:
            The schema or None if not found
        """
        ...

    def hasSchema(self, key: str) -> bool:
        """
        Check if a schema exists.

        Args:
            key: Schema key

        Returns:
            True if the schema exists
        """
        ...

    def save(self) -> None:
        """Save configuration to persistent storage."""
        ...


@runtime_checkable
class StorageController(Protocol):
    """Storage controller for creating device/plugin storage."""

    def createCameraStorage(
        self, instance: Any, cameraId: str, schemas: list[JsonSchema] | None = None
    ) -> DeviceStorage:
        """
        Create storage for a camera.

        Args:
            instance: Plugin instance
            cameraId: Camera ID
            schemas: Optional initial schemas

        Returns:
            Device storage instance
        """
        ...

    def createPluginStorage(self, instance: Any, schemas: list[JsonSchema] | None = None) -> DeviceStorage:
        """
        Create storage for a plugin.

        Args:
            instance: Plugin instance
            schemas: Optional initial schemas

        Returns:
            Device storage instance
        """
        ...

    def getCameraStorage(self, camera_id: str) -> DeviceStorage | None:
        """
        Get storage for a camera.

        Args:
            camera_id: Camera ID

        Returns:
            Device storage or None if not found
        """
        ...

    def getPluginStorage(self) -> DeviceStorage | None:
        """
        Get storage for the plugin.

        Returns:
            Device storage or None if not found
        """
        ...
