"""JSON Schema types for plugin configuration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Generic, Literal, Required, TypeAlias, TypedDict, TypeVar, Union

# ============ JSON TYPES ============

# Note: Using Union instead of | for recursive type aliases (forward references don't work with | at runtime)
JSONValue: TypeAlias = dict[str, Union[str, int, float, bool, "JSONValue", list["JSONValue"]]]
JSONObject: TypeAlias = dict[str, JSONValue]
JSONArray: TypeAlias = list[JSONValue]
Path = list[int | str] | int | str

PluginConfig = dict[str, Any]

OnSetCallback = (
    Callable[[Any, Any], None | Any]
    | Callable[[Any, Any], Awaitable[None | Any]]
    | Callable[[Any, Any], Coroutine[Any, Any, None | Any]]
)

OnGetCallback = (
    Callable[[], None | Any]
    | Callable[[], Awaitable[None | Any]]
    | Callable[[], Coroutine[Any, Any, None | Any]]
)

# ============ SCHEMA TYPE LITERALS ============

JsonSchemaType = Literal["string", "number", "boolean", "array", "button", "submit"]

StringFormat = Literal[
    "date-time", "date", "time", "email", "uuid", "ipv4", "ipv6", "password", "qrCode", "image"
]

ButtonColor = Literal["success", "info", "warn", "danger"]

# ============ GENERIC TYPE VARIABLE ============

T = TypeVar(
    "T",
    str,
    int,
    float,
    bool,
    list[str],
    list[int],
    list[float],
    list[bool],
    # For enum with multiple=True
    str | list[str],
)


# ============ BASE SCHEMAS ============


class JsonFactorySchema(TypedDict):
    """Base schema factory type - required fields for all schemas."""

    type: JsonSchemaType
    key: str
    title: str
    description: str


class JsonBaseSchemaWithoutCallbacks(JsonFactorySchema, Generic[T], total=False):
    """Base schema without callbacks - generic over defaultValue type."""

    group: str
    hidden: bool
    required: bool
    readonly: bool
    placeholder: str
    defaultValue: T


class JsonBaseSchema(JsonBaseSchemaWithoutCallbacks[T], Generic[T], total=False):
    """Base schema with callbacks - generic over defaultValue type."""

    store: bool
    onSet: OnSetCallback
    onGet: OnGetCallback


# ============ TYPE-SPECIFIC SCHEMAS ============


class JsonStringSchema(TypedDict, total=False):
    """String-specific schema properties."""

    type: Literal["string"]
    format: StringFormat
    minLength: int
    maxLength: int


class JsonNumberSchema(TypedDict, total=False):
    """Number-specific schema properties."""

    type: Literal["number"]
    minimum: int | float
    maximum: int | float
    step: int | float


class JsonBooleanSchema(TypedDict):
    """Boolean-specific schema properties."""

    type: Literal["boolean"]


class JsonEnumSchema(TypedDict, total=False):
    """Enum-specific schema properties."""

    type: Literal["string"]
    enum: list[str]
    multiple: bool


class JsonArraySchema(TypedDict, total=False):
    """Array-specific schema properties."""

    type: Literal["array"]
    opened: bool
    items: JsonSchemaWithoutCallbacks


# ============ COMBINED SCHEMA TYPES (WITH CALLBACKS) ============


class JsonSchemaString(JsonBaseSchema[str], total=False):
    """Complete string schema."""

    type: Required[Literal["string"]]  # type: ignore
    format: StringFormat
    minLength: int
    maxLength: int


class JsonSchemaNumber(JsonBaseSchema[int | float], total=False):
    """Complete number schema."""

    type: Required[Literal["number"]]  # type: ignore
    minimum: int | float
    maximum: int | float
    step: int | float


class JsonSchemaBoolean(JsonBaseSchema[bool], total=False):
    """Complete boolean schema."""

    type: Required[Literal["boolean"]]  # type: ignore


class JsonSchemaEnum(JsonBaseSchema[str | list[str]], total=False):
    """Complete enum schema."""

    type: Required[Literal["string"]]  # type: ignore
    enum: Required[list[str]]
    multiple: bool


class JsonSchemaArray(JsonBaseSchema[list[str] | list[int] | list[float] | list[bool]], total=False):  # pyright: ignore[reportInvalidTypeArguments]
    """Complete array schema."""

    type: Required[Literal["array"]]  # type: ignore
    opened: bool
    items: JsonSchemaWithoutCallbacks


class JsonSchemaButton(TypedDict, total=False):
    """Button schema - triggers an action."""

    type: Required[Literal["button"]]
    key: Required[str]
    title: Required[str]
    description: Required[str]
    onSet: OnSetCallback
    group: str
    color: ButtonColor


class JsonSchemaSubmit(TypedDict, total=False):
    """Submit schema - form submission with response."""

    type: Required[Literal["submit"]]
    key: Required[str]
    title: Required[str]
    description: Required[str]
    onClick: Required[Callable[[Any], Awaitable[FormSubmitResponse | None]]]
    group: str
    color: ButtonColor


# ============ COMBINED SCHEMA TYPES (WITHOUT CALLBACKS) ============


class JsonSchemaStringWithoutCallbacks(JsonBaseSchemaWithoutCallbacks[str], total=False):
    """String schema without callbacks."""

    type: Required[Literal["string"]]  # type: ignore
    format: StringFormat
    minLength: int
    maxLength: int


class JsonSchemaNumberWithoutCallbacks(JsonBaseSchemaWithoutCallbacks[int | float], total=False):
    """Number schema without callbacks."""

    type: Required[Literal["number"]]  # type: ignore
    minimum: int | float
    maximum: int | float
    step: int | float


class JsonSchemaBooleanWithoutCallbacks(JsonBaseSchemaWithoutCallbacks[bool], total=False):
    """Boolean schema without callbacks."""

    type: Required[Literal["boolean"]]  # type: ignore


class JsonSchemaEnumWithoutCallbacks(JsonBaseSchemaWithoutCallbacks[str | list[str]], total=False):
    """Enum schema without callbacks."""

    type: Required[Literal["string"]]  # type: ignore
    enum: Required[list[str]]
    multiple: bool


class JsonSchemaArrayWithoutCallbacks(
    JsonBaseSchemaWithoutCallbacks[list[str] | list[int] | list[float] | list[bool]],  # pyright: ignore[reportInvalidTypeArguments]
    total=False,
):
    """Array schema without callbacks."""

    type: Required[Literal["array"]]  # type: ignore
    opened: bool
    items: JsonSchemaWithoutCallbacks


# ============ UNION TYPES ============

JsonSchema = (
    JsonSchemaString
    | JsonSchemaNumber
    | JsonSchemaBoolean
    | JsonSchemaEnum
    | JsonSchemaArray
    | JsonSchemaButton
    | JsonSchemaSubmit
)

JsonSchemaWithoutKey = (
    JsonSchemaStringWithoutCallbacks
    | JsonSchemaNumberWithoutCallbacks
    | JsonSchemaBooleanWithoutCallbacks
    | JsonSchemaEnumWithoutCallbacks
)

JsonSchemaWithoutCallbacks = (
    JsonSchemaStringWithoutCallbacks
    | JsonSchemaNumberWithoutCallbacks
    | JsonSchemaBooleanWithoutCallbacks
    | JsonSchemaEnumWithoutCallbacks
    | JsonSchemaArrayWithoutCallbacks
)


# ============ RESPONSE TYPES ============


class ToastMessage(TypedDict):
    """Toast notification message."""

    type: Literal["info", "success", "warning", "error"]
    message: str


class FormSubmitSchema(TypedDict):
    """Form submit schema."""

    config: dict[str, Any]


class FormSubmitResponse(TypedDict, total=False):
    """Form submit response."""

    toast: ToastMessage
    schema: list[JsonSchemaWithoutCallbacks]


class SchemaConfig(TypedDict):
    """Schema configuration."""

    schema: list[JsonSchema]
    config: dict[str, Any]
