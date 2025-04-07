# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import List, Optional, Tuple

from .base import (
    BaseDeviceState,
)
from .base_focuser import (
    BaseFocuserDeviceInterface,
    BaseFocuserDeviceParameters,
    BaseFocuserMode,
    BaseFocuserMovingState,
)
from .client import PlaneWaveHTTPXClient
from .response import (
    ResponsePlanTextParserToJSON as ResponseParser,
)
from .status import PlaneWaveFocuserDeviceInterfaceStatus
from .version import PlaneWaveDeviceInterfaceVersion

# **************************************************************************************


class PlaneWaveFocuserDeviceParameters(BaseFocuserDeviceParameters):
    name: str
    description: str


# **************************************************************************************


class PlaneWaveFocuserDeviceInterface(BaseFocuserDeviceInterface):
    """
    Abstract class representing a generic focuser device.

    This class extends the BaseDeviceInterface by adding methods and properties
    specific to focusers, such as getting and setting the focuser position, checking
    if the focuser is moving, and returning the current focuser mode.

    Subclasses should override these methods with the appropriate hardware-specific logic.
    """

    _id: int = 0

    # The mode of the focuser:
    _mode: BaseFocuserMode = BaseFocuserMode.ABSOLUTE

    # The moving state of the focuser
    _moving_state: BaseFocuserMovingState = BaseFocuserMovingState.IDLE

    # Is the focuser enabled?
    _is_enabled: bool = False

    _target_step_position: int = 0

    def __init__(
        self,
        id: int,
        params: PlaneWaveFocuserDeviceParameters,
        client: Optional[PlaneWaveHTTPXClient],
    ) -> None:
        """
        Initialise the base focuser interface.

        Args:
            params (Optional[PlaneWaveFocuserDeviceParameters]): An optional dictionary-like object
                containing device parameters such as vendor ID (vid), product ID (pid),
                or device ID (did).
        """
        super().__init__(params)
        # The name of the focuser (default: "PlaneWave Focuser"):
        self._name = params.get("name", "PlaneWave Focuser")

        # The description of the mount (default: "PlaneWave Mount Interface (HTTP)"):
        self._description = params.get(
            "description", "PlaneWave Mount Interface (HTTP)"
        )

        # Set the identifier for the device:
        self._id = id

        if not client:
            client = PlaneWaveHTTPXClient(host="localhost", port=8220)

        self._client = client._client

    @property
    def id(self) -> int:
        """
        Unique identifier for the device.

        Returns:
            int: The unique device identifier.
        """
        return self._id

    def initialise(self, timeout: float = 5.0, retries: int = 3) -> None:
        """
        Initialise the device.

        This method should handle any necessary setup required before the device can be used.
        """

        # Define the initialisation function to be run in a separate thread:
        def do_initialise() -> None:
            if self.state == BaseDeviceState.CONNECTED:
                return

            # We leave the device state as DISCONNECTED until connect() is called:
            self.state = BaseDeviceState.DISCONNECTED

            # We leave the slewing state as IDLE until a slewing operation is initiated:
            self._moving_state = BaseFocuserMovingState.IDLE

            # If we have a device ID, attempt to connect:
            self.connect(timeout=timeout, retries=retries)

            # Get the status of the mount from the device:
            status = self.get_status()

            if not status:
                raise RuntimeError("Status not available")

        # Keep a track of the number of attempts:
        i = 0

        # Try to initialise the mount up to `retries` times, with the given timeout:
        while i < retries:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(do_initialise)
                try:
                    # Block for up to `timeout` seconds to see if init completes
                    future.result(timeout=timeout)
                    return
                except TimeoutError:
                    # If we have a timeout after the retries are exhausted, raise an exception:
                    if i == retries - 1:
                        raise TimeoutError(
                            f"[Mount ID {self.id}]: Did not initialize within {timeout} seconds "
                            f"after {retries} attempts."
                        )
                except RuntimeError as error:
                    # If we have a runtime error after the retries are exhausted, raise it:
                    if i == retries - 1:
                        raise error

            # Increment the retry counter:
            i += 1

    def reset(self) -> None:
        """
        Reset the device.

        This method should restore the device to its default or initial state.
        """
        # Reset the device state to DISCONNECTED:
        self.disconnect()

        # Re-initialise the device:
        self.initialise()

    def connect(self, timeout: float = 5.0, retries: int = 3) -> None:
        """
        Establish a connection to the device.

        This method should implement the operations required to connect to the device.
        """
        if self.state == BaseDeviceState.CONNECTED:
            return

        response = self._client.get(url="/focuser/enable")

        response.raise_for_status()

        self.state = BaseDeviceState.CONNECTED

    def disconnect(self) -> None:
        """
        Disconnect from the device.

        This method should handle any cleanup or shutdown procedures necessary to safely
        disconnect from the device.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return

        self.abort_move()

        response = self._client.get(url="/focuser/disable")

        response.raise_for_status()

        self.state = BaseDeviceState.DISCONNECTED

    def get_status(self) -> Optional[PlaneWaveFocuserDeviceInterfaceStatus]:
        """
        Get the current status of the device.

        Returns:
            PlaneWaveMountDeviceInterfaceStatus: The current status of the device.

        Raises:
            HTTPStatusError: If the status data is invalid or missing
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        response = self._client.get(url="/status")

        response.raise_for_status()

        data = ResponseParser(response.read()).parse()

        return PlaneWaveFocuserDeviceInterfaceStatus.model_validate(data)

    def is_connected(self) -> bool:
        """
        Check if the device is connected.

        Returns:
            bool: True if the device is connected; otherwise, False.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        status = self.get_status()

        if not status:
            return False

        return (
            True
            if self.state == BaseDeviceState.CONNECTED and status.is_connected
            else False
        )

    def is_ready(self) -> bool:
        """
        Check if the device is ready for operation.

        Returns:
            bool: True if the device is ready; otherwise, False.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        status = self.get_status()

        if not status:
            return False

        return (
            True
            if self.state == BaseDeviceState.CONNECTED
            and status.is_connected
            and status.is_enabled
            and not status.is_moving
            else False
        )

    def get_name(self) -> str:
        """
        Get the name of the device.

        Returns:
            str: The device name. The default is "BaseDevice".
        """
        return self._name

    def get_description(self) -> str:
        """
        Get a description of the device.

        Returns:
            str: A brief description of the device. Defaults to an empty string.
        """
        return self._description

    def get_driver_version(self) -> Tuple[int, int, int]:
        """
        Get the version of the device driver as a tuple (major, minor, patch).

        Returns:
            Tuple[int, int, int]: The driver version. Defaults to (0, 0, 0).
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return 0, 0, 0

        response = self._client.get(url="/status")

        response.raise_for_status()

        data = ResponseParser(response.read()).parse()

        model = PlaneWaveDeviceInterfaceVersion.model_validate(data)

        return model.version

    def get_firmware_version(self) -> Tuple[int, int, int]:
        """
        Get the version of the device firmware as a tuple (major, minor, patch).

        Returns:
            Tuple[int, int, int]: The firmware version. Defaults to (0, 0, 0).
        """
        raise NotImplementedError("get_firmware_version() not implemented.")

    def get_capabilities(self) -> List[str]:
        """
        Retrieve a list of capabilities supported by the device.

        Returns:
            List[str]: A list of capability names. Defaults to an empty list.
        """
        raise NotImplementedError("get_capabilities() not implemented.")

    def get_mode(self) -> BaseFocuserMode:
        """
        Retrieve the current mode of the focuser.

        Returns:
            BaseFocuserMode: The current mode of the focuser.
        """
        return self._mode

    def is_moving(self) -> bool:
        """
        Check if the focuser is currently moving.

        Returns:
            bool: True if the focuser is moving, False otherwise.
        """
        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        return (
            status.is_moving
            and self._moving_state == BaseFocuserMovingState.MOVING
            and self._target_step_position != status.position
        )

    def is_absolute(self) -> bool:
        """
        Check if the focuser is in absolute mode.

        Returns:
            bool: True if the focuser is in absolute mode, False otherwise.
        """
        return self._mode == BaseFocuserMode.ABSOLUTE

    def is_enabled(self) -> bool:
        """
        Check if the focuser is enabled.

        Returns:
            bool: True if the focuser is enabled, False otherwise.
        """
        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        self._is_enabled = status.is_enabled

        return status.is_enabled and self._is_enabled

    def get_position(self) -> int:
        """
        Get the current position of the focuser.

        Returns:
            int: The current position of the focuser.
        """
        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        if status.position is None:
            raise RuntimeError("Position not available")

        return status.position

    def set_position(self, position: int) -> None:
        """
        Set the position of the focuser.

        Args:
            position (int): The desired position of the focuser.
        """
        self._target_step_position = position

        response = self._client.get(
            url="/focuser/goto",
            params={
                "target": position,
            },
        )

        response.raise_for_status()

    def abort_move(self) -> None:
        """
        Abort any ongoing movement of the focuser.
        """
        response = self._client.get(url="/focuser/stop")

        response.raise_for_status()


# **************************************************************************************
