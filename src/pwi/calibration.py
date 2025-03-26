# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from typing import List, NotRequired, TypedDict

from celerity.coordinates import HorizontalCoordinate

from .common import NumericRange

# **************************************************************************************


class HorizontalCalibrationParameters(TypedDict):
    """
    The parameters for a horizontal mount calibration procedure.
    """

    # The range of altitudes to calibrate (e.g., from 0° to 90°):
    altitude_range: NumericRange
    # The number of altitude points to sample between the minimum and maximum altitude:
    number_of_altitude_points: NotRequired[int]
    # The number of azimuth points to sample from 0° up to (but not including) 360°:
    number_of_azimuth_points: NotRequired[int]


# **************************************************************************************

DEFAULT_HORIZONTAL_CALIBRATION_PARAMETERS = HorizontalCalibrationParameters(
    {
        "altitude_range": NumericRange(minimum=30.0, maximum=90.0),
        "number_of_altitude_points": 6,
        "number_of_azimuth_points": 24,
    }
)

# **************************************************************************************


def get_horizontal_calibration_coordinates(
    params: HorizontalCalibrationParameters = DEFAULT_HORIZONTAL_CALIBRATION_PARAMETERS,
) -> List[HorizontalCoordinate]:
    """
    Generate a list of horizontal coordinates for a calibration procedure based on
    the given input parameters.

    The resulting list of coordinates will be a series of points that sweep across the
    sky in the most efficient way possible, given the number of altitude and azimuth points
    specified. The slew time between each point should be minimised, whereby the points
    are distributed in a way that minimises the total slew time required to calibrate the
    mount.

    Args:
        params (HorizontalCalibrationParameters): The parameters for the horizontal calibration.

    Returns:
        List[HorizontalCoordinate]: A list of horizontal coordinates.

    Raises:
        ValueError:
            - If number_of_altitude_points < 1.
            - If number_of_azimuth_points < 1.
            - If minimum_altitude > maximum_altitude.
    """
    # Get the number of altitudinal points from the parameters:
    number_of_altitude_points = params.get("number_of_altitude_points", 6)

    # Ensure the number of altitude points is at least 1:
    if number_of_altitude_points < 1:
        raise ValueError("number_of_altitude_points must be at least 1.")

    # Get the number of azimuth points from the parameters:
    number_of_azimuth_points = params.get("number_of_azimuth_points", 24)

    # Ensure the number of azimuth points is at least 1:
    if number_of_azimuth_points < 1:
        raise ValueError("number_of_azimuth_points must be at least 1.")

    # Get the altidudinal range from the parameters:
    altitudinal_range = params.get(
        "altitude_range", NumericRange(minimum=0.0, maximum=90.0)
    )

    # Get the minimum altitude from the range:
    minimum_altitude = altitudinal_range.get("minimum", 30.0)

    # Get the maximum altitude from the range:
    maximum_altitude = altitudinal_range.get("maximum", 90.0)

    # Ensure minimum altitude is less than or equal to maximum altitude:
    if minimum_altitude > maximum_altitude:
        raise ValueError("minimum_altitude must be <= maximum_altitude.")

    # Calculate the altitude step size (in degrees):
    altitude_step = (maximum_altitude - minimum_altitude) / max(
        number_of_altitude_points - 1, 1
    )

    # Calculate the azimuth step size (in degrees):
    azimuth_step = 360.0 / number_of_azimuth_points

    # Create a list of altitude values from min to max (inclusive):
    altitudes_ascending = [
        minimum_altitude + i * altitude_step for i in range(number_of_altitude_points)
    ]

    # Create a reversed list of the same altitudes, for descending altitude values:
    altitudes_descending = list(reversed(altitudes_ascending))

    points: List[HorizontalCoordinate] = []

    for index in range(number_of_azimuth_points):
        az = index * azimuth_step

        # For even index, we sweep from the minimum to maximum altitude:
        if index % 2 == 0:
            for alt in altitudes_ascending:
                points.append(HorizontalCoordinate(alt=alt, az=az))
        # For odd index, we sweep from the maximum to minimum altitude:
        else:
            for alt in altitudes_descending:
                points.append(HorizontalCoordinate(alt=alt, az=az))

    # Return the list of horizontal coordinates:
    return points


# **************************************************************************************
