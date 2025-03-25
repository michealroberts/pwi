# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from enum import Enum

# **************************************************************************************


class BaseMountAlignmentMode(Enum):
    """
    Enumeration of possible mount alignment modes.
    """

    UNKNOWN = "unknown"
    EQUATORIAL = "equatorial"
    HORIZONTAL = "horizontal"
    ALT_AZ = "alt_az"
    POLAR = "polar"
    GERMAN_POLAR = "german_polar"


# **************************************************************************************


class BaseMountTrackingMode(Enum):
    """
    Enumeration of possible mount tracking modes.
    """

    SIDEREAL = "sidereal"
    SOLAR = "solar"
    LUNAR = "lunar"
    CUSTOM = "custom"


# **************************************************************************************


class BaseMountSlewingState(Enum):
    """
    Enumeration of possible mount slewing states.
    """

    IDLE = "idle"
    SLEWING = "slewing"
    SETTLING = "settling"


# **************************************************************************************


class BaseMountTrackingState(Enum):
    """
    Enumeration of possible mount tracking states.
    """

    IDLE = "idle"
    TRACKING = "tracking"


# **************************************************************************************
