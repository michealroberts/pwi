# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timezone
from math import inf
from time import sleep
from typing import Dict, List, Literal, Optional, Tuple, TypedDict

from celerity.coordinates import (
    EquatorialCoordinate,
    HorizontalCoordinate,
)
from celerity.refraction import get_correction_to_horizontal_for_refraction

from .axis import PlaneWaveDeviceInterfaceAxis
from .base import (
    BaseDeviceState,
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
from .client import PlaneWaveHTTPXClient
from .offsets import PlaneWaveDeviceInterfaceOffsets
from .response import (
    ResponsePlanTextParserToJSON as ResponseParser,
)
from .site import PlaneWaveDeviceInterfaceSite
from .status import PlaneWaveDeviceInterfaceStatus
from .units import convert_arcseconds_to_degrees
from .version import PlaneWaveDeviceInterfaceVersion

# **************************************************************************************


class PlaneWaveMountDeviceParameters(BaseMountDeviceParameters):
    name: str
    description: str
    alignment: Literal[BaseMountAlignmentMode.ALT_AZ, BaseMountAlignmentMode.EQUATORIAL]


# **************************************************************************************


class EquatorialCoordinateAtTime(EquatorialCoordinate):
    at: Optional[datetime]


# **************************************************************************************


class HorizontalCoordinateAtTime(HorizontalCoordinate):
    at: Optional[datetime]


# **************************************************************************************


class PlaneWaveMountDeviceAxisTelemetry(TypedDict):
    # The root mean square (RMS) error (in arcseconds):
    rms_error: Optional[float]
    # The distance to the target (in degrees):
    distance_to_target: Optional[float]
    # The servo error (in arcseconds):
    servo_error: Optional[float]
    # The minimum mechanical position (in degrees):
    minimum_mechanical_position: Optional[float]
    # The maximum mechanical position (in degrees):
    maximum_mechanical_position: Optional[float]
    # The target mechanical position (in degrees):
    target_mechanical_position: Optional[float]
    # The current mechanical position (in degrees):
    mechanical_position: Optional[float]
    # The timestamp of the last mechanical position update:
    last_mechanical_position_datetime: Optional[datetime]
    # The maximum velocity (in degrees per second):
    maximum_velocity: Optional[float]
    # The setpoint velocity (in degrees per second):
    setpoint_velocity: Optional[float]
    # The measured velocity (in degrees per second):
    measured_velocity: Optional[float]
    # The acceleration (in degrees per second squared):
    acceleration: Optional[float]
    # The measured current (in amps):
    measured_current_amps: Optional[float]


# **************************************************************************************


class PlaneWaveMountDeviceAzimuthalTelemetry(PlaneWaveMountDeviceAxisTelemetry):
    ra: float
    az: float


# **************************************************************************************


class PlaneWaveMountDevicePolarTelemetry(PlaneWaveMountDeviceAxisTelemetry):
    dec: float
    alt: float


# **************************************************************************************


class PlaneWaveMountDeviceTelemetry(TypedDict):
    # The UTC time of the telemetry data:
    utc: datetime
    # The azimuth axis (e.g., azimuth or RA) telemetry:
    azimuth: PlaneWaveMountDeviceAzimuthalTelemetry
    # The polar axis (e.g., altitude or declination) telemetry:
    polar: PlaneWaveMountDevicePolarTelemetry


# **************************************************************************************


class PlaneWaveMountDeviceInterface(BaseMountDeviceInterface):
    """
    PlaneWaveMountDeviceInterface is a concrete implementation of BaseMountDeviceInterface
    for PlaneWave mounts. It provides a simple interface to control PlaneWave mounts
    over HTTP using the PlaneWave HTTP API using the HTTPX library.
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
    _alignment_mode: BaseMountAlignmentMode = BaseMountAlignmentMode.ALT_AZ

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

    # The target equatorial coordinate of the mount for slewing operations:
    _target_equatorial_coordinate: EquatorialCoordinate = EquatorialCoordinate(
        {
            "ra": 0.0,
            "dec": 0.0,
        }
    )

    # The target horizontal coordinate of the mount for slewing operations:
    _target_horizontal_coordinate: HorizontalCoordinate = HorizontalCoordinate(
        {
            "alt": 0.0,
            "az": 0.0,
        }
    )

    # The home position of the mount:
    home: HorizontalCoordinate = HorizontalCoordinate(
        {
            "az": 0.0,
            "alt": 90.0,
        }
    )

    # The park position of the mount:
    park: HorizontalCoordinate = HorizontalCoordinate(
        {
            "az": 0.0,
            "alt": 15.0,
        }
    )

    # Does the mount automatically adjust for atmospheric refraction?
    _does_refraction: bool = True

    # The list of calibration points for the mount:
    _indices: List[int] = []

    def __init__(
        self,
        id: int,
        params: PlaneWaveMountDeviceParameters,
        client: Optional[PlaneWaveHTTPXClient],
    ) -> None:
        """
        Initialise the base mount interface.

        Args:
            params (Optional[PlaneWaveMountDeviceParameters]): An optional dictionary-like object
                containing device parameters such as vendor ID (vid), product ID (pid),
                or device ID (did).
        """
        super().__init__(params)
        # The name of the mount (default: "PlaneWave Mount"):
        self._name = params.get("name", "PlaneWave Mount")

        # The description of the mount (default: "PlaneWave Mount Interface (HTTP)"):
        self._description = params.get(
            "description", "PlaneWave Mount Interface (HTTP)"
        )
        # The alignment mode of the mount (default: ALT_AZ):
        self._alignment_mode = params.get("alignment", BaseMountAlignmentMode.ALT_AZ)

        # Set the site geographic coordinates (latitude, longitude, elevation) of the mount:
        self._latitude = params.get("latitude", 0.0)
        self._longitude = params.get("longitude", 0.0)
        self._elevation = params.get("elevation", 0.0)

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
            self._slewing_state = BaseMountSlewingState.IDLE

            # We leave the tracking state as IDLE until tracking is started:
            self._tracking_state = BaseMountTrackingState.IDLE

            # If we have a device ID, attempt to connect:
            self.connect(timeout=timeout, retries=retries)

            # Get the status of the mount from the device:
            status = self.get_status()

            if not status:
                raise RuntimeError("Status not available")

            self.enable_axis(axis=0)

            self.enable_axis(axis=1)

            site = self.get_site()

            if not site:
                raise RuntimeError("Site information not available")

            self._latitude = site.latitude if site.latitude else self._latitude
            self._longitude = site.longitude if site.longitude else self._longitude
            self._elevation = site.elevation if site.elevation else self._elevation
            self._LMST = site.lmst

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

        response = self._client.get(url="/mount/connect")

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

        self.abort_slew()

        self.abort_tracking()

        self.disable_axis(axis=0)

        self.disable_axis(axis=1)

        response = self._client.get(url="/mount/disconnect")

        response.raise_for_status()

        self.state = BaseDeviceState.DISCONNECTED

    def get_status(self) -> Optional[PlaneWaveDeviceInterfaceStatus]:
        """
        Get the current status of the device.

        Returns:
            PlaneWaveDeviceInterfaceStatus: The current status of the device.

        Raises:
            HTTPStatusError: If the status data is invalid or missing
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        response = self._client.get(url="/status")

        response.raise_for_status()

        data = ResponseParser(response.read()).parse()

        return PlaneWaveDeviceInterfaceStatus.model_validate(data)

    def get_site(self) -> Optional[PlaneWaveDeviceInterfaceSite]:
        """
        Get the site information for the device.

        Returns:
            PlaneWaveDeviceInterfaceSite: The site information

        Raises:
            HTTPStatusError: If the site data is invalid or missing
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        response = self._client.get(url="/status")

        response.raise_for_status()

        data = ResponseParser(response.read()).parse()

        return PlaneWaveDeviceInterfaceSite.model_validate(data)

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
            and not status.is_slewing
            and not status.is_tracking
            else False
        )

    def get_name(self) -> str:
        """
        Get the name of the device.

        Returns:
            str: The device name.
        """
        return self._name

    def get_description(self) -> str:
        """
        Get a description of the device.

        Returns:
            str: A brief description of the device.
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
        raise NotImplementedError("Firmware version not available")

    def get_capabilities(self) -> List[str]:
        """
        Retrieve a list of capabilities supported by the device.

        Returns:
            List[str]: A list of capability names. Defaults to an empty list.
        """
        raise NotImplementedError("Capabilities not available")

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

    def can_find_home(self) -> bool:
        """
        Check if the mount supports homing procedures.

        Returns:
            bool: True if the mount supports homing, False otherwise.
        """
        return True

    def is_home(self) -> bool:
        """
        Check if the mount is currently at the home position.

        Returns:
            bool: True if the mount is at the home position, False otherwise.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        status = self.get_status()

        mount = PlaneWaveDeviceInterfaceStatus.model_validate(status)

        if not mount.horizontal_coordinate:
            return False

        tolerance = 0.1  # 0.1 degree of tolerance

        return (
            abs(mount.horizontal_coordinate["az"] - self.home["az"]) <= tolerance
            and abs(mount.horizontal_coordinate["alt"] - self.home["alt"]) <= tolerance
        )

    async def find_home(self) -> None:
        """
        Initiate a homing procedure to move the mount to the home position.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return

        response = self._client.get(url="/mount/find_home")

        response.raise_for_status()

        while not self.is_home():
            # Sleep for 100 milliseconds:
            sleep(0.1)

        self.abort_slew()

        self.abort_tracking()

    def set_park(self, horizontal: HorizontalCoordinate) -> None:
        """
        Set the park position of the mount.

        Args:
            horizontal (HorizontalCoordinate): The park position.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        self.stop_tracking()

        # Assume the HorizontalCoordinate has keys "alt" and "az" (in degrees):
        params = {"alt_degs": horizontal.get("alt"), "az_degs": horizontal.get("az")}

        response = self._client.get(url="/mount/goto_alt_az", params=params)

        response.raise_for_status()

        while not self.is_parked():
            # Sleep for 100 milliseconds:
            sleep(0.1)

        response = self._client.get(url="/mount/set_park_here")

        response.raise_for_status()

        # Set the park position of the mount to the specified horizontal coordinate:
        self.park = horizontal

    def can_park(self) -> bool:
        """
        Check if the mount supports parking procedures.

        Returns:
            bool: True if the mount supports parking, False otherwise.
        """
        return True

    def is_parked(self):
        """
        Check if the mount is currently at the park position.

        Returns:
            bool: True if the mount is at the park position, False otherwise.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        status = self.get_status()

        mount = PlaneWaveDeviceInterfaceStatus.model_validate(status)

        if not mount.horizontal_coordinate:
            return False

        tolerance = 0.1  # 0.1 degree of tolerance

        return (
            abs(mount.horizontal_coordinate["az"] - self.park["az"]) <= tolerance
            and abs(mount.horizontal_coordinate["alt"] - self.park["alt"]) <= tolerance
        )

    def find_park(self) -> bool:
        """
        Initiate a parking procedure to move the mount to the park position.

        Returns:
            bool: True if the mount is parked, False otherwise.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        response = self._client.get(url="/mount/park")

        response.raise_for_status()

        while not self.is_parked():
            # Sleep for 100 milliseconds:
            sleep(0.1)

        self.abort_slew()

        self.abort_tracking()

        return True

    def get_right_ascension(
        self, epoch: Literal["J2000", "apparent"] = "J2000"
    ) -> float:
        """
        Retrieve the current right ascension coordinate of the mount.

        Returns:
            float: The current right ascension coordinate (in degrees).
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return inf

        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        if not status.j2000_equatorial_coordinate:
            raise RuntimeError("J2000 equatorial coordinate not available")

        if not status.apparent_equatorial_coordinate:
            raise RuntimeError("Apparent equatorial coordinate not available")

        return (
            status.j2000_equatorial_coordinate.get("ra", inf)
            if epoch == "J2000"
            else status.apparent_equatorial_coordinate.get("ra", inf)
        )

    def get_declination(self, epoch: Literal["J2000", "apparent"] = "J2000") -> float:
        """
        Retrieve the current declination coordinate of the mount.

        Returns:
            float: The current declination coordinate (in degrees).
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return inf

        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        if not status.j2000_equatorial_coordinate:
            raise RuntimeError("J2000 equatorial coordinate not available")

        if not status.apparent_equatorial_coordinate:
            raise RuntimeError("Apparent equatorial coordinate not available")

        return (
            status.j2000_equatorial_coordinate.get("dec", inf)
            if epoch == "J2000"
            else status.apparent_equatorial_coordinate.get("dec", inf)
        )

    def get_equatorial_coordinate(
        self, epoch: Literal["J2000", "apparent"] = "J2000"
    ) -> Optional[EquatorialCoordinateAtTime]:
        """
        Retrieve the current equatorial coordinate of the mount.

        Args:
            epoch: The epoch for the equatorial coordinate ("J2000" or "apparent").

        Returns:
            EquatorialCoordinateAtTime: The current equatorial coordinate.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        if not status.j2000_equatorial_coordinate:
            raise RuntimeError("J2000 equatorial coordinate not available")

        if not status.apparent_equatorial_coordinate:
            raise RuntimeError("Apparent equatorial coordinate not available")

        equatorial: EquatorialCoordinate = (
            status.j2000_equatorial_coordinate
            if epoch == "J2000"
            else status.apparent_equatorial_coordinate
        )

        return EquatorialCoordinateAtTime(
            {
                "ra": equatorial.get("ra", inf),
                "dec": equatorial.get("dec", inf),
                "at": status.utc,
            }
        )

    def get_altitude(self) -> float:
        """
        Retrieve the current altitude coordinate of the mount.

        Returns:
            float: The current altitude coordinate (in degrees).
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return inf

        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        if not status.horizontal_coordinate:
            raise RuntimeError("Horizontal coordinate not available")

        return status.horizontal_coordinate.get("alt", inf)

    def get_azimuth(self) -> float:
        """
        Retrieve the current azimuth coordinate of the mount.

        Returns:
            float: The current azimuth coordinate (in degrees).
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return inf

        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        if not status.horizontal_coordinate:
            raise RuntimeError("Horizontal coordinate not available")

        return status.horizontal_coordinate.get("az", inf)

    def get_horizontal_coordinate(self) -> Optional[HorizontalCoordinateAtTime]:
        """
        Retrieve the current horizontal coordinate of the mount.

        Returns:
            HorizontalCoordinateAtTime: The current horizontal coordinate.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        if not status.horizontal_coordinate:
            raise RuntimeError("Horizontal coordinate not available")

        return HorizontalCoordinateAtTime(
            {
                "alt": status.horizontal_coordinate.get("alt", inf),
                "az": status.horizontal_coordinate.get("az", inf),
                "at": status.utc,
            }
        )

    def get_topocentric_coordinate(self) -> Optional[HorizontalCoordinateAtTime]:
        """
        Retrieve the current topocentric coordinate of the mount.

        Returns:
            HorizontalCoordinate: The current topocentric coordinate.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        # Get the current status of the mount:
        status = self.get_status()

        # If the status is not available, return None:
        if not status:
            raise RuntimeError("Status not available")

        # If the horizontal coordinate is not available, return None:
        if not status.horizontal_coordinate:
            raise RuntimeError("Horizontal coordinate not available")

        # Assume the HorizontalCoordinate has keys "alt" and "az" (in degrees):
        return HorizontalCoordinateAtTime(
            {
                "alt": status.horizontal_coordinate.get("alt", inf),
                "az": status.horizontal_coordinate.get("az", inf),
                "at": status.utc,
            }
        )

    def get_telemetry(
        self,
    ) -> Optional[PlaneWaveMountDeviceTelemetry]:
        """
        Retrieve the positional telemetry of the mount, such as current pointing position,
        tracking rate, axes error, and other relevant information.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        response = self._client.get(url="/status")

        response.raise_for_status()

        data = ResponseParser(response.read()).parse()

        status = PlaneWaveDeviceInterfaceStatus.model_validate(data)

        axis0 = data.copy()

        # Inject the axis number into data to help model validator know which axis to extract:
        axis0["axis_number"] = 0

        axis_azimuthal = PlaneWaveDeviceInterfaceAxis.model_validate(axis0)

        axis1 = data.copy()

        # Inject the axis number into data to help model validator know which axis to extract:
        axis1["axis_number"] = 1

        axis_polar = PlaneWaveDeviceInterfaceAxis.model_validate(axis1)

        now: datetime = status.utc if status.utc else datetime.now(tz=timezone.utc)

        equatorial: EquatorialCoordinate = EquatorialCoordinate(
            {
                "ra": status.j2000_equatorial_coordinate.get("ra", inf)
                if status.j2000_equatorial_coordinate
                else inf,
                "dec": status.j2000_equatorial_coordinate.get("dec", inf)
                if status.j2000_equatorial_coordinate
                else inf,
            }
        )

        horizontal: HorizontalCoordinate = HorizontalCoordinate(
            {
                "alt": status.horizontal_coordinate.get("alt", inf)
                if status.horizontal_coordinate
                else inf,
                "az": status.horizontal_coordinate.get("az", inf)
                if status.horizontal_coordinate
                else inf,
            }
        )

        azimuth_axis_telemetry = PlaneWaveMountDeviceAzimuthalTelemetry(
            ra=equatorial["ra"],
            az=horizontal["az"],
            rms_error=convert_arcseconds_to_degrees(axis_azimuthal.rms_error or 0.0),
            distance_to_target=convert_arcseconds_to_degrees(
                axis_azimuthal.distance_to_target or inf
            ),
            servo_error=convert_arcseconds_to_degrees(
                axis_azimuthal.servo_error or 0.0
            ),
            minimum_mechanical_position=axis_azimuthal.minimum_mechanical_position,
            maximum_mechanical_position=axis_azimuthal.maximum_mechanical_position,
            target_mechanical_position=axis_azimuthal.target_mechanical_position,
            mechanical_position=axis_azimuthal.mechanical_position,
            last_mechanical_position_datetime=axis_azimuthal.last_mechanical_position_datetime,
            maximum_velocity=axis_azimuthal.maximum_velocity,
            setpoint_velocity=axis_azimuthal.setpoint_velocity,
            measured_velocity=axis_azimuthal.measured_velocity,
            acceleration=axis_azimuthal.acceleration,
            measured_current_amps=axis_azimuthal.measured_current_amps,
        )

        polar_axis_telemetry = PlaneWaveMountDevicePolarTelemetry(
            dec=equatorial["dec"],
            alt=horizontal["alt"],
            rms_error=convert_arcseconds_to_degrees(axis_polar.rms_error or 0.0),
            distance_to_target=convert_arcseconds_to_degrees(
                axis_polar.distance_to_target or inf
            ),
            servo_error=convert_arcseconds_to_degrees(axis_polar.servo_error or 0.0),
            minimum_mechanical_position=axis_polar.minimum_mechanical_position,
            maximum_mechanical_position=axis_polar.maximum_mechanical_position,
            target_mechanical_position=axis_polar.target_mechanical_position,
            mechanical_position=axis_polar.mechanical_position,
            last_mechanical_position_datetime=axis_polar.last_mechanical_position_datetime,
            maximum_velocity=axis_polar.maximum_velocity,
            setpoint_velocity=axis_polar.setpoint_velocity,
            measured_velocity=axis_polar.measured_velocity,
            acceleration=axis_polar.acceleration,
            measured_current_amps=axis_polar.measured_current_amps,
        )

        return PlaneWaveMountDeviceTelemetry(
            {
                "utc": now,
                "azimuth": azimuth_axis_telemetry,
                "polar": polar_axis_telemetry,
            }
        )

    def get_slew_rate(self) -> float:
        """
        Retrieve the current slew rate of the mount.

        Returns:
            float: The current slew rate (in degrees per second).
        """
        return 0.0

    def get_slew_settle_time(self) -> float:
        """
        Retrieve the current slew settle time of the mount.

        Returns:
            float: The current slew settle time (in seconds).
        """
        return 1.5

    def is_slewing(self) -> bool:
        """
        Check if the mount is currently slewing.

        Returns:
            bool: True if the mount is slewing, False otherwise.
        """
        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        return (
            status.is_slewing and self._slewing_state == BaseMountSlewingState.SLEWING
        )

    def is_horizontal(self) -> bool:
        """
        Check if the mount is currently in topocentric mode.

        Returns:
            bool: True if the mount is in topocentric mode, False otherwise.
        """
        return (
            self._alignment_mode == BaseMountAlignmentMode.ALT_AZ
            or self._alignment_mode == BaseMountAlignmentMode.HORIZONTAL
        )

    def is_equatorial(self) -> bool:
        """
        Check if the mount is currently in equatorial mode.

        Returns:
            bool: True if the mount is in equatorial mode, False otherwise.
        """
        return (
            self._alignment_mode == BaseMountAlignmentMode.EQUATORIAL
            or self._alignment_mode == BaseMountAlignmentMode.POLAR
            or self._alignment_mode == BaseMountAlignmentMode.GERMAN_POLAR
        )

    def has_slewed_to_target(self, tolerance: float = 0.1) -> bool:
        """
        Check if the mount has successfully slewed to the target coordinate.

        Returns:
            bool: True if the mount has successfully slewed to the target, False otherwise.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        status = self.get_status()

        mount = PlaneWaveDeviceInterfaceStatus.model_validate(status)

        if not mount.horizontal_coordinate or not mount.apparent_equatorial_coordinate:
            return False

        return (
            (
                abs(
                    mount.horizontal_coordinate["az"]
                    - self._target_horizontal_coordinate["az"]
                )
                <= tolerance
                and abs(
                    mount.horizontal_coordinate["alt"]
                    - self._target_horizontal_coordinate["alt"]
                )
                <= tolerance
            )
            if self.is_horizontal()
            else (
                abs(
                    mount.apparent_equatorial_coordinate["ra"]
                    - self._target_equatorial_coordinate["ra"]
                )
                <= tolerance
                and abs(
                    mount.apparent_equatorial_coordinate["dec"]
                    - self._target_equatorial_coordinate["dec"]
                )
                <= tolerance
            )
        )

    def does_refraction(self) -> bool:
        """
        Check if the mount is currently compensating for atmospheric refraction.

        Returns:
            bool: True if the mount is compensating for refraction, False otherwise.
        """
        return self._does_refraction

    def get_axis(
        self, axis: Literal[0, 1] = 0
    ) -> Optional[PlaneWaveDeviceInterfaceAxis]:
        """
        Get the status of the specified axis of the mount.

        Args:
            axis (int): The axis to query (0 or 1).

        Returns:
            PlaneWaveDeviceInterfaceAxis: The status of the specified axis.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        response = self._client.get(url="/status")

        response.raise_for_status()

        data = ResponseParser(response.read()).parse()

        # Inject the axis number into data to help model validator know which axis to extract
        data["axis_number"] = axis

        return PlaneWaveDeviceInterfaceAxis.model_validate(data)

    def enable_axis(self, axis: Literal[0, 1] = 0) -> None:
        """
        Enable the specified axis of the mount.

        Args:
            axis (int): The axis to enable (0 or 1).
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return

        response = self._client.get(url="/mount/enable", params={"axis": axis})

        response.raise_for_status()

    def disable_axis(self, axis: Literal[0, 1] = 0) -> None:
        """
        Disable the specified axis of the mount.

        Args:
            axis (int): The axis to disable (0 or 1).
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return

        response = self._client.get(url="/mount/disable", params={"axis": axis})

        response.raise_for_status()

    def get_offsets(self) -> Optional[PlaneWaveDeviceInterfaceOffsets]:
        """
        Retrieve the current offsets for the mount.

        Returns:
            PlaneWaveDeviceInterfaceOffsets: The current offsets for the mount.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return None

        response = self._client.get(url="/mount/offsets")

        response.raise_for_status()

        data = ResponseParser(response.read()).parse()

        return PlaneWaveDeviceInterfaceOffsets.model_validate(data)

    async def slew_to_equatorial_coordinate(
        self,
        equatorial: EquatorialCoordinate,
        epoch: Literal["J2000", "apparent"] = "J2000",
    ) -> bool:
        """
        Slew the mount to the specified equatorial coordinate.

        Args:
            equatorial (EquatorialCoordinate): The target equatorial coordinate.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        # Store the target equatorial coordinate for future reference:
        self._target_equatorial_coordinate = equatorial

        # Choose the appropriate endpoint based on the epoch.
        url = (
            "/mount/goto_ra_dec_j2000"
            if epoch == "J2000"
            else "/mount/goto_ra_dec_apparent"
        )

        # Assume the EquatorialCoordinate has keys "ra" and "dec"
        params = {"ra_hours": equatorial.get("ra"), "dec_degs": equatorial.get("dec")}

        response = self._client.get(url=url, params=params)

        response.raise_for_status()

        self._slewing_state = BaseMountSlewingState.SETTLING

        sleep(self.get_slew_settle_time())

        self._slewing_state = BaseMountSlewingState.IDLE

        return True

    async def slew_to_horizontal_coordinate(
        self,
        horizontal: HorizontalCoordinate,
        temperature: float = 283.15,
        pressure: float = 101325,
    ) -> bool:
        """
        Slew the mount to the specified topocentric coordinate.

        Args:
            topocentric (TopocentricCoordinate): The target topocentric coordinate.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        # Correct the horizontal coordinate for atmospheric refraction:
        horizontal = get_correction_to_horizontal_for_refraction(
            target=horizontal, temperature=temperature, pressure=pressure
        )

        return await self.slew_to_topocentric_coordinate(topocentric=horizontal)

    async def slew_to_topocentric_coordinate(
        self, topocentric: HorizontalCoordinate
    ) -> bool:
        """
        Slew the mount to the specified topocentric coordinate.

        An alias of `slew_to_horizontal_coordinate`.

        Args:
            topocentric (TopocentricCoordinate): The target topocentric coordinate.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        # Store the target horizontal coordinate for future reference:
        self._target_horizontal_coordinate = topocentric

        # Assume the HorizontalCoordinate has keys "alt" and "az" (in degrees):
        params = {"alt_degs": topocentric.get("alt"), "az_degs": topocentric.get("az")}

        response = self._client.get(url="/mount/goto_alt_az", params=params)

        response.raise_for_status()

        return True

    def abort_slew(self) -> None:
        """
        Abort any ongoing slewing operation.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return

        response = self._client.get(url="/mount/stop")

        response.raise_for_status()

        self._slewing_state = BaseMountSlewingState.IDLE

    def is_tracking(self) -> bool:
        """
        Check if the mount is currently tracking.

        Returns:
            bool: True if the mount is tracking, False otherwise.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return False

        status = self.get_status()

        if not status:
            raise RuntimeError("Status not available")

        return (
            status.is_tracking
            and self._tracking_state == BaseMountTrackingState.TRACKING
        )

    def start_tracking(self) -> None:
        """
        Start tracking the mount with the default tracking rate.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return

        response = self._client.get(url="/mount/tracking_on")

        response.raise_for_status()

        self._tracking_state = BaseMountTrackingState.TRACKING

    def stop_tracking(self) -> None:
        """
        Stop tracking the mount.
        """
        if self.state == BaseDeviceState.DISCONNECTED:
            return

        response = self._client.get(url="/mount/tracking_off")

        response.raise_for_status()

        self._tracking_state = BaseMountTrackingState.IDLE

    def get_tracking_state(self) -> BaseMountTrackingState:
        """Return the current tracking state."""
        if self.state == BaseDeviceState.DISCONNECTED:
            return BaseMountTrackingState.IDLE

        status = self.get_status()

        if not status:
            raise RuntimeError("Tracking state not available")

        return (
            BaseMountTrackingState.IDLE
            if not status.is_tracking
            else self._tracking_state
        )

    async def sync_to_equatorial_coordinate(
        self, equatorial: EquatorialCoordinate
    ) -> None:
        """
        Slew and synchronise the mount to the specified equatorial coordinate.

        Args:
            equatorial (EquatorialCoordinate): The target equatorial coordinate.
        """
        await self.slew_to_equatorial_coordinate(equatorial)

        while not self.has_slewed_to_target():
            await asyncio.sleep(0.1)

        if not self.is_tracking():
            self.start_tracking()

    async def sync_to_horizontal_coordinate(
        self, horizontal: HorizontalCoordinate
    ) -> None:
        """
        Slew and synchronise the mount to the specified topocentric coordinate.

        Args:
            topocentric (TopocentricCoordinate): The target topocentric coordinate.
        """
        await self.slew_to_horizontal_coordinate(horizontal)

        while not self.has_slewed_to_target():
            await asyncio.sleep(0.1)

        if not self.is_tracking():
            self.start_tracking()

    async def sync_to_topocentric_coordinates(
        self, topocentric: HorizontalCoordinate
    ) -> None:
        """
        Slew and synchronise the mount to the specified topocentric coordinate.

        An alias of `sync_to_horizontal_coordinate`.

        Args:
            topocentric (TopocentricCoordinate): The target topocentric coordinate.
        """
        await self.slew_to_topocentric_coordinate(topocentric)

        if self.is_tracking():
            return

        self.start_tracking()

    async def sync_to_tle(self, tle: str) -> None:
        """
        Slew and synchronise the mount to the specified TLE.

        Args:
            tle (str): The target TLE.
        """
        # [TBD] Implement a TLE parsing process to validate the TLE here.

    def get_tracking_rate(self) -> float:
        """
        Retrieve the current tracking rate of the mount.

        Returns:
            float: The current tracking rate (in sidereal seconds per sidereal second).
        """
        return 0.0

    def set_tracking_rate(self, rate: float) -> None:
        """
        Set the tracking rate of the mount.

        Args:
            rate (float): The desired tracking rate (in sidereal seconds per sidereal second).
        """
        pass

    def abort_tracking(self) -> None:
        """
        Abort any ongoing tracking operation.
        """
        response = self._client.get(url="/mount/tracking_off")

        response.raise_for_status()

        self._tracking_state = BaseMountTrackingState.IDLE

    def model_add_point(self, point: EquatorialCoordinate) -> None:
        """
        Add a point to the pointing model.

        Args:
            point (EquatorialCoordinate): The equatorial coordinate to add to the model.
        """
        ra = point.get("ra", 0.0)

        params = {
            "ra_j2000_hours": ra / 15.0,
            "dec_j2000_degs": point.get("dec", 0.0),
        }

        response = self._client.get(
            url="/mount/model/add_point",
            params=params,
        )

        response.raise_for_status()

    def model_delete_point(self, indices: List[int]) -> None:
        """
        Delete a point from the pointing model by its index.

        Args:
            index (int): The index of the point to delete.
        """
        index = ",".join([str(x) for x in indices])

        response = self._client.get(
            url="/mount/model/delete_point",
            params={"index": index},
        )

        response.raise_for_status()

    def model_enable_point(self, indices: List[int]) -> None:
        """
        Enable a point in the pointing model by its index.

        Args:
            index (int): The index of the point to enable.
        """
        index = ",".join([str(x) for x in indices])

        response = self._client.get(
            url="/mount/model/enable_point",
            params={"index": index},
        )

        response.raise_for_status()

    def model_disable_point(self, indices: List[int]) -> None:
        """
        Disable a point in the pointing model by its index.

        Args:
            index (int): The index of the point to disable.
        """
        index = ",".join([str(x) for x in indices])

        response = self._client.get(
            url="/mount/model/disable_point",
            params={"index": index},
        )

        response.raise_for_status()

    def model_clear_points(self):
        """ "
        Clear all points from the pointing model.
        """
        response = self._client.get(url="/mount/model/clear_points")

        response.raise_for_status()

    def model_save(self, filename: str) -> None:
        """
        Save the active pointing model to a file so that it can later be re-loaded.

        Args:
            filename (Path): The filename to save the model to (default: "active.model").
        """
        response = self._client.get(
            url="/mount/model/save", params={"filename": filename}
        )

        response.raise_for_status()

    def model_save_as_default(self) -> None:
        """
        Save the active pointing model to a file so that it can later be re-loaded as the default model.
        """
        response = self._client.get(url="/mount/model/save_as_default")

        response.raise_for_status()

    def model_load(self, filename: str) -> None:
        """
        Load the pointing model from a file.

        Args:
            filename (Path): The filename to load the model from (default: "active.model").
        """
        response = self._client.get(
            url="/mount/model/load", params={"filename": filename}
        )

        response.raise_for_status()


# **************************************************************************************
