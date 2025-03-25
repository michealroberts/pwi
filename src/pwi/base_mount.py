# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from abc import abstractmethod
from enum import Enum
from typing import Dict, Optional, TypedDict

from celerity.coordinates import EquatorialCoordinate, HorizontalCoordinate

from .base import BaseDeviceInterface, BaseDeviceParameters

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


class BaseMountDeviceParameters(BaseDeviceParameters):
    latitude: float
    longitude: float
    elevation: float


# **************************************************************************************


class BaseMountCalibrationPoint(TypedDict):
    target: EquatorialCoordinate
    mechanical: EquatorialCoordinate
    active: bool


# **************************************************************************************


class BaseMountDeviceInterface(BaseDeviceInterface):
    """
    Abstract class representing a generic mount device.

    This class extends the BaseDeviceInterface by adding methods and properties
    specific to mounts, such as initiating slewing motions, executing tracking,
    performing alignment procedures, and handling common mount parameters like
    tracking rates, slew speeds, and coordinate adjustments.

    Subclasses should override these methods with the appropriate hardware-specific logic.
    """

    _id: int = 0

    # The latitude of the mount (in degrees):
    _latitude: float = 0.0

    # The longitude of the mount (in degrees):
    _longitude: float = 0.0

    # The elevation of the mount (in meters):
    _elevation: float = 0.0

    # The right ascension coordinate of the mount:
    _ra: float = 0.0

    # The declination coordinate of the mount:
    _dec: float = 0.0

    # The altitude coordinate of the mount:
    _altitude: float = 0.0

    # The azimuth coordinate of the mount:
    _azimuth: float = 0.0

    # The alignment mode of the mount:
    _alignment_mode: BaseMountAlignmentMode = BaseMountAlignmentMode.EQUATORIAL

    # The tracking mode of the mount:
    _tracking_mode: BaseMountTrackingMode = BaseMountTrackingMode.SIDEREAL

    # The slewing state of the mount:
    _slewing_state: BaseMountSlewingState = BaseMountSlewingState.IDLE

    # The tracking state of the mount:
    _tracking_state: BaseMountTrackingState = BaseMountTrackingState.IDLE

    # The default calibration model for the mount:
    _default_calibration_model: Dict[int, BaseMountCalibrationPoint] = {}

    # The current alignment mode of the mount:
    _calibration_points: Dict[int, BaseMountCalibrationPoint] = {}

    # Does the mount automatically adjust for atmospheric refraction?
    _does_refraction: bool = False

    def __init__(self, params: Optional[BaseMountDeviceParameters] = None) -> None:
        """
        Initialise the base mount interface.

        Args:
            params (Optional[BaseMountDeviceParameters]): An optional dictionary-like object
                containing device parameters such as vendor ID (vid), product ID (pid),
                or device ID (did).
        """
        super().__init__(params)

        if not params:
            return

        self._latitude = params.get("latitude", 0.0)
        self._longitude = params.get("longitude", 0.0)
        self._elevation = params.get("elevation", 0.0)

    def get_alignment_mode(self) -> BaseMountAlignmentMode:
        """
        Retrieve the current alignment mode of the mount.

        Returns:
            str: The current alignment mode.
        """
        return self._alignment_mode

    def get_tracking_mode(self) -> BaseMountTrackingMode:
        """
        Retrieve the current tracking mode of the mount.

        Returns:
            str: The current tracking mode.
        """
        return self._tracking_mode

    @abstractmethod
    def can_find_home(self) -> bool:
        """
        Check if the mount supports homing procedures.

        Returns:
            bool: True if the mount supports homing, False otherwise.
        """
        return False

    @abstractmethod
    def is_home(self) -> bool:
        """
        Check if the mount is currently at the home position.

        Returns:
            bool: True if the mount is at the home position, False otherwise.
        """
        return False

    @abstractmethod
    async def find_home(self) -> None:
        """
        Initiate a homing procedure to move the mount to the home position.
        """
        pass

    @abstractmethod
    def get_right_ascension(self) -> float:
        """
        Retrieve the current right ascension coordinate of the mount.

        Returns:
            float: The current right ascension coordinate (in degrees).
        """
        return 0.0

    @abstractmethod
    def get_declination(self) -> float:
        """
        Retrieve the current declination coordinate of the mount.

        Returns:
            float: The current declination coordinate (in degrees).
        """
        return 0.0

    @abstractmethod
    def get_altitude(self) -> float:
        """
        Retrieve the current altitude coordinate of the mount.

        Returns:
            float: The current altitude coordinate (in degrees).
        """
        return 0.0

    @abstractmethod
    def get_azimuth(self) -> float:
        """
        Retrieve the current azimuth coordinate of the mount.

        Returns:
            float: The current azimuth coordinate (in degrees).
        """
        return 0.0

    @abstractmethod
    def get_slew_rate(self) -> float:
        """
        Retrieve the current slew rate of the mount.

        Returns:
            float: The current slew rate (in degrees per second).
        """
        return 0.0

    @abstractmethod
    def get_slew_settle_time(self) -> float:
        """
        Retrieve the current slew settle time of the mount.

        Returns:
            float: The current slew settle time (in seconds).
        """
        return 0.0

    @abstractmethod
    def is_slewing(self) -> bool:
        """
        Check if the mount is currently slewing.

        Returns:
            bool: True if the mount is slewing, False otherwise.
        """
        return False

    @abstractmethod
    def does_refraction(self) -> bool:
        """
        Check if the mount is currently compensating for atmospheric refraction.

        Returns:
            bool: True if the mount is compensating for refraction, False otherwise.
        """
        return self._does_refraction

    @abstractmethod
    async def slew_to_equatorial_coordinate(
        self, equatorial: EquatorialCoordinate
    ) -> bool:
        """
        Slew the mount to the specified equatorial coordinate.

        Args:
            equatorial (EquatorialCoordinate): The target equatorial coordinate.
        """
        pass

    @abstractmethod
    async def slew_to_horizontal_coordinate(
        self, horizontal: HorizontalCoordinate
    ) -> bool:
        """
        Slew the mount to the specified topocentric/horizontal coordinate.

        Args:
            horizontal (HorizontalCoordinate): The target horizontal coordinate.
        """
        pass

    @abstractmethod
    async def slew_to_topocentric_coordinate(
        self, topocentric: HorizontalCoordinate
    ) -> bool:
        """
        Slew the mount to the specified topocentric/horizontal coordinate.

        An alias of `slew_to_horizontal_coordinate`.

        Args:
            topocentric (TopocentricCoordinate): The target topocentric coordinate.
        """
        pass

    @abstractmethod
    def abort_slew(self) -> None:
        """
        Abort any ongoing slewing operation.
        """
        pass

    @abstractmethod
    def is_tracking(self) -> bool:
        """
        Check if the mount is currently tracking.

        Returns:
            bool: True if the mount is tracking, False otherwise.
        """
        return False

    @abstractmethod
    async def sync_to_equatorial_coordinate(
        self, equatorial: EquatorialCoordinate
    ) -> None:
        """
        Slew and synchronise the mount to the specified equatorial coordinate.

        Args:
            equatorial (EquatorialCoordinate): The target equatorial coordinate.
        """
        pass

    @abstractmethod
    async def sync_to_horizontal_coordinate(
        self, horizontal: HorizontalCoordinate
    ) -> None:
        """
        Slew and synchronise the mount to the specified topocentric coordinate.

        Args:
            topocentric (TopocentricCoordinate): The target topocentric coordinate.
        """
        pass

    @abstractmethod
    async def sync_to_topocentric_coordinates(
        self, topocentric: HorizontalCoordinate
    ) -> None:
        """
        Slew and synchronise the mount to the specified topocentric coordinate.

        An alias of `sync_to_horizontal_coordinate`.

        Args:
            topocentric (TopocentricCoordinate): The target topocentric coordinate.
        """
        pass

    @abstractmethod
    async def sync_to_tle(self, tle: str) -> None:
        """
        Slew and synchronise the mount to the specified TLE.

        Args:
            tle (str): The target TLE.
        """
        pass

    @abstractmethod
    def get_tracking_rate(self) -> float:
        """
        Retrieve the current tracking rate of the mount.

        Returns:
            float: The current tracking rate (in degrees per second).
        """
        return 0.0

    @abstractmethod
    def set_tracking_rate(self, rate: float) -> None:
        """
        Set the tracking rate of the mount.

        Args:
            rate (float): The desired tracking rate (in degrees per second).
        """
        pass

    @abstractmethod
    def abort_tracking(self) -> None:
        """
        Abort any ongoing tracking operation.
        """
        pass


# **************************************************************************************
