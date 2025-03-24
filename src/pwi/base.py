# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Tuple, TypedDict

from pwi.utils import is_hexadecimal

# **************************************************************************************


class BaseDeviceParameters(TypedDict):
    did: Optional[str]
    vid: Optional[str]
    pid: Optional[str]


# **************************************************************************************


class BaseDeviceState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


# **************************************************************************************


class BaseDeviceInterface(ABC):
    # Class-level attributes for device-specific identifiers.
    # Subclasses may use these as defaults.

    # Vendor ID
    vid: Optional[str] = None
    # Product ID
    pid: Optional[str] = None
    # Device ID (e.g., to differentiate devices with the same vid and pid):
    did: Optional[str] = None

    # The current state of the device:
    state: BaseDeviceState = BaseDeviceState.DISCONNECTED

    def __init__(self, params: Optional[BaseDeviceParameters]) -> None:
        if not params:
            return

        self.vid = params.get("vid", None)
        self.pid = params.get("pid", None)
        self.did = params.get("did", None)

    @property
    def device_id(self) -> str:
        """
        Unique identifier for the device.

        Returns:
            str: The unique device identifier.
        """
        return self.did or "BaseDevice"

    @property
    def vendor_id(self) -> str:
        """
        Optional vendor identifier.

        Returns:
            str: The vendor identifier. Defaults to an empty string.
        """
        if not self.vid:
            return ""

        return (
            f"0x{int(self.vid, 16):04x}" if is_hexadecimal(self.vid) else f"{self.vid}"
        )

    @property
    def product_id(self) -> str:
        """
        Optional product identifier.

        Returns:
            str: The product identifier. Defaults to an empty string.
        """
        if not self.pid:
            return ""

        return (
            f"0x{int(self.pid, 16):04x}" if is_hexadecimal(self.pid) else f"{self.pid}"
        )

    @abstractmethod
    def initialise(self, timeout: float = 5.0, retries: int = 3) -> None:
        """
        Initialise the device.

        This method should handle any necessary setup required before the device can be used.
        """
        raise NotImplementedError("initialise() not implemented.")

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the device.

        This method should restore the device to its default or initial state.
        """
        raise NotImplementedError("reset() not implemented.")

    @abstractmethod
    def connect(self, timeout: float = 5.0, retries: int = 3) -> None:
        """
        Establish a connection to the device.

        This method should implement the operations required to connect to the device.
        """
        raise NotImplementedError("connect() not implemented.")

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from the device.

        This method should handle any cleanup or shutdown procedures necessary to safely
        disconnect from the device.
        """
        raise NotImplementedError("disconnect() not implemented.")

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the device is connected.

        Returns:
            bool: True if the device is connected; otherwise, False.
        """
        return True if self.state == BaseDeviceState.CONNECTED else False

    @abstractmethod
    def is_ready(self) -> bool:
        """
        Check if the device is ready for operation.

        Returns:
            bool: True if the device is ready; otherwise, False.
        """
        raise NotImplementedError("is_ready() not implemented.")

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the device.

        Returns:
            str: The device name. The default is "BaseDevice".
        """
        raise NotImplementedError("get_name() not implemented.")

    @abstractmethod
    def get_description(self) -> str:
        """
        Get a description of the device.

        Returns:
            str: A brief description of the device. Defaults to an empty string.
        """
        raise NotImplementedError("get_description() not implemented.")

    @abstractmethod
    def get_driver_version(self) -> Tuple[int, int, int]:
        """
        Get the version of the device driver as a tuple (major, minor, patch).

        Returns:
            Tuple[int, int, int]: The driver version. Defaults to (0, 0, 0).
        """
        raise NotImplementedError("get_driver_version() not implemented.")

    @abstractmethod
    def get_firmware_version(self) -> Tuple[int, int, int]:
        """
        Get the version of the device firmware as a tuple (major, minor, patch).

        Returns:
            Tuple[int, int, int]: The firmware version. Defaults to (0, 0, 0).
        """
        raise NotImplementedError("get_firmware_version() not implemented.")

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Retrieve a list of capabilities supported by the device.

        Returns:
            List[str]: A list of capability names. Defaults to an empty list.
        """
        raise NotImplementedError("get_capabilities() not implemented.")


# **************************************************************************************
