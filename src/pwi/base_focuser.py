# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from enum import Enum

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
