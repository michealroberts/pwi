# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from .axis import PlaneWaveMountDeviceInterfaceAxis
from .base import (
    BaseDeviceInterface,
    BaseDeviceParameters,
    BaseDeviceState,
)
from .base_focuser import (
    BaseFocuserDeviceInterface,
    BaseFocuserDeviceParameters,
    BaseFocuserMode,
    BaseFocuserMovingState,
)
from .base_mount import (
    BaseMountAlignmentMode,
    BaseMountCalibrationPoint,
    BaseMountDeviceInterface,
    BaseMountDeviceParameters,
    BaseMountSlewingState,
    BaseMountTrackingMode,
    BaseMountTrackingState,
)
from .calibration import (
    HorizontalCalibrationParameters,
    get_horizontal_calibration_coordinates,
)
from .client import PlaneWaveHTTPXClient
from .mount import (
    EquatorialCoordinateAtTime,
    HorizontalCoordinateAtTime,
    PlaneWaveMountDeviceInterface,
    PlaneWaveMountDeviceParameters,
    PlaneWaveMountDeviceTelemetry,
)
from .offsets import PlaneWaveMountDeviceInterfaceOffsets
from .serial import is_device_connected_over_usb
from .site import PlaneWaveMountDeviceInterfaceSite
from .status import PlaneWaveMountDeviceInterfaceStatus

# **************************************************************************************

__version__ = "0.13.0"

# **************************************************************************************

__license__ = "MIT"

# **************************************************************************************

VENDOR_ID = "1cbe"

# **************************************************************************************

PRODUCT_ID = "0267"

# **************************************************************************************

__all__: list[str] = [
    "__license__",
    "__version__",
    "VENDOR_ID",
    "PRODUCT_ID",
    "get_horizontal_calibration_coordinates",
    "is_device_connected_over_usb",
    "BaseDeviceInterface",
    "BaseDeviceParameters",
    "BaseDeviceState",
    "BaseFocuserDeviceInterface",
    "BaseFocuserDeviceParameters",
    "BaseFocuserMode",
    "BaseFocuserMovingState",
    "BaseMountAlignmentMode",
    "BaseMountCalibrationPoint",
    "BaseMountDeviceInterface",
    "BaseMountDeviceParameters",
    "BaseMountSlewingState",
    "BaseMountTrackingMode",
    "BaseMountTrackingState",
    "EquatorialCoordinateAtTime",
    "HorizontalCoordinateAtTime",
    "HorizontalCalibrationParameters",
    "PlaneWaveMountDeviceInterfaceAxis",
    "PlaneWaveMountDeviceInterfaceOffsets",
    "PlaneWaveMountDeviceInterfaceSite",
    "PlaneWaveMountDeviceInterfaceStatus",
    "PlaneWaveHTTPXClient",
    "PlaneWaveMountDeviceInterface",
    "PlaneWaveMountDeviceParameters",
    "PlaneWaveMountDeviceTelemetry",
]

# **************************************************************************************
