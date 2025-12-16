"""Sensor module exports."""

# Base
# Audio
from .audio import (
    AudioDetectorSensor,
    AudioDetectorSensorLike,
    AudioProperty,
    AudioSensor,
    AudioSensorLike,
)
from .base import PropertyChangeListener, Sensor, SensorLike

# Battery
from .battery import (
    BatteryCapability,
    BatteryInfo,
    BatteryInfoLike,
    BatteryProperty,
)

# Contact
from .contact import (
    ContactProperty,
    ContactSensor,
    ContactSensorLike,
)

# Doorbell
from .doorbell import (
    DoorbellProperty,
    DoorbellTrigger,
    DoorbellTriggerLike,
)

# Face
from .face import (
    FaceDetectorSensor,
    FaceDetectorSensorLike,
    FaceProperty,
    FaceSensor,
    FaceSensorLike,
)

# Guards
from .guards import (
    isAudioSensor,
    isBatteryInfo,
    isContactSensor,
    isDoorbellTrigger,
    isFaceSensor,
    isLicensePlateSensor,
    isLightControl,
    isMotionSensor,
    isObjectSensor,
    isPTZControl,
    isSecuritySystem,
    isSirenControl,
    isSwitchControl,
)

# License Plate
from .license_plate import (
    LicensePlateDetectorSensor,
    LicensePlateDetectorSensorLike,
    LicensePlateProperty,
    LicensePlateSensor,
    LicensePlateSensorLike,
)

# Light
from .light import (
    LightCapability,
    LightControl,
    LightControlLike,
    LightProperty,
)

# Motion
from .motion import (
    MotionDetectorSensor,
    MotionDetectorSensorLike,
    MotionProperty,
    MotionSensor,
    MotionSensorLike,
)

# Object
from .object import (
    ObjectDetectorSensor,
    ObjectDetectorSensorLike,
    ObjectProperty,
    ObjectSensor,
    ObjectSensorLike,
)

# PTZ
from .ptz import (
    PTZCapability,
    PTZControl,
    PTZControlLike,
    PTZProperty,
)

# Security System
from .security_system import (
    SecuritySystem,
    SecuritySystemLike,
    SecuritySystemProperty,
    SecuritySystemState,
)

# Siren
from .siren import (
    SirenCapability,
    SirenControl,
    SirenControlLike,
    SirenProperty,
)

# Switch
from .switch import (
    SwitchControl,
    SwitchControlLike,
    SwitchProperty,
)

# Types
from .types import (
    AudioInputProperties,
    BoundingBox,
    ChargingState,
    Detection,
    FaceDetection,
    FaceLandmarks,
    LicensePlateDetection,
    ObjectClassLabel,
    PropertyChangedEvent,
    PTZDirection,
    PTZPosition,
    SensorAddedEvent,
    SensorCapabilitiesChangedEvent,
    SensorCategory,
    SensorRefreshedState,
    SensorRemovedEvent,
    SensorType,
    StoredSensorData,
    VideoInputProperties,
)

SensorPropertyType = (
    AudioProperty
    | BatteryProperty
    | ContactProperty
    | DoorbellProperty
    | FaceProperty
    | LicensePlateProperty
    | LightProperty
    | MotionProperty
    | ObjectProperty
    | PTZProperty
    | SecuritySystemProperty
    | SirenProperty
    | SwitchProperty
)
"""Union type of all sensor property enums."""

SensorCapability = PTZCapability | LightCapability | SirenCapability | BatteryCapability
"""Union type of all sensor capability enums."""

__all__ = [
    # Base
    "Sensor",
    "SensorLike",
    "PropertyChangeListener",
    # Types
    "SensorPropertyType",
    "SensorCapability",
    "AudioInputProperties",
    "BoundingBox",
    "ChargingState",
    "Detection",
    "FaceDetection",
    "FaceLandmarks",
    "LicensePlateDetection",
    "ObjectClassLabel",
    "PropertyChangedEvent",
    "PTZDirection",
    "PTZPosition",
    "SensorAddedEvent",
    "SensorCapabilitiesChangedEvent",
    "SensorCategory",
    "SensorRefreshedState",
    "SensorRemovedEvent",
    "SensorType",
    "StoredSensorData",
    "VideoInputProperties",
    # Motion
    "MotionProperty",
    "MotionSensorLike",
    "MotionDetectorSensorLike",
    "MotionSensor",
    "MotionDetectorSensor",
    # Object
    "ObjectProperty",
    "ObjectSensorLike",
    "ObjectDetectorSensorLike",
    "ObjectSensor",
    "ObjectDetectorSensor",
    # Audio
    "AudioProperty",
    "AudioSensorLike",
    "AudioDetectorSensorLike",
    "AudioSensor",
    "AudioDetectorSensor",
    # Face
    "FaceProperty",
    "FaceSensorLike",
    "FaceDetectorSensorLike",
    "FaceSensor",
    "FaceDetectorSensor",
    # License Plate
    "LicensePlateProperty",
    "LicensePlateSensorLike",
    "LicensePlateDetectorSensorLike",
    "LicensePlateSensor",
    "LicensePlateDetectorSensor",
    # Contact
    "ContactProperty",
    "ContactSensorLike",
    "ContactSensor",
    # Light
    "LightCapability",
    "LightProperty",
    "LightControlLike",
    "LightControl",
    # Siren
    "SirenCapability",
    "SirenProperty",
    "SirenControlLike",
    "SirenControl",
    # Switch
    "SwitchProperty",
    "SwitchControlLike",
    "SwitchControl",
    # PTZ
    "PTZCapability",
    "PTZProperty",
    "PTZControlLike",
    "PTZControl",
    # Security System
    "SecuritySystem",
    "SecuritySystemLike",
    "SecuritySystemProperty",
    "SecuritySystemState",
    # Doorbell
    "DoorbellProperty",
    "DoorbellTriggerLike",
    "DoorbellTrigger",
    # Battery
    "BatteryCapability",
    "BatteryProperty",
    "BatteryInfoLike",
    "BatteryInfo",
    # Guards
    "isMotionSensor",
    "isObjectSensor",
    "isAudioSensor",
    "isFaceSensor",
    "isLicensePlateSensor",
    "isContactSensor",
    "isLightControl",
    "isSirenControl",
    "isSwitchControl",
    "isPTZControl",
    "isSecuritySystem",
    "isDoorbellTrigger",
    "isBatteryInfo",
]
