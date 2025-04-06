# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from abc import abstractmethod
from enum import Enum
from typing import Optional

from .base import BaseDeviceInterface, BaseDeviceParameters

# **************************************************************************************


class BaseFocuserMode(Enum):
    """
    Enumeration of possible focuser modes.
    """

    RELATIVE = "relative"
    ABSOLUTE = "absolute"


# **************************************************************************************


class BaseFocuserMovingState(Enum):
    """
    Enumeration of possible focuser moving states.
    """

    IDLE = "idle"
    MOVING = "moving"


# **************************************************************************************


class BaseFocuserDeviceParameters(BaseDeviceParameters):
    pass


# **************************************************************************************


class BaseFocuserDeviceInterface(BaseDeviceInterface):
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

    def __init__(self, params: Optional[BaseFocuserDeviceParameters] = None) -> None:
        """
        Initialise the base focuser interface.

        Args:
            params (Optional[BaseFocuserDeviceParameters]): An optional dictionary-like object
                containing device parameters such as vendor ID (vid), product ID (pid),
                or device ID (did).
        """
        super().__init__(params)

        if not params:
            return

        self._latitude = params.get("latitude", 0.0)
        self._longitude = params.get("longitude", 0.0)
        self._elevation = params.get("elevation", 0.0)

    def is_moving(self) -> bool:
        """
        Check if the focuser is currently moving.

        Returns:
            bool: True if the focuser is moving, False otherwise.
        """
        return self._moving_state == BaseFocuserMovingState.MOVING

    def get_mode(self) -> BaseFocuserMode:
        """
        Retrieve the current mode of the focuser.

        Returns:
            BaseFocuserMode: The current mode of the focuser (absolute or relative).
        """
        return self._mode

    def is_enabled(self) -> bool:
        """
        Check if the focuser is enabled.

        Returns:
            bool: True if the focuser is enabled, False otherwise.
        """
        return self._is_enabled

    @abstractmethod
    def get_position(self) -> int:
        """
        Get the current position of the focuser.

        Returns:
            int: The current position of the focuser.
        """
        raise NotImplementedError("get_position() must be implemented by the subclass.")

    @abstractmethod
    def set_position(self, position: int) -> None:
        """
        Set the position of the focuser.

        Args:
            position (int): The desired position of the focuser.
        """
        raise NotImplementedError("set_position() must be implemented by the subclass.")


# **************************************************************************************
