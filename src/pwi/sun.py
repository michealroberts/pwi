# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from datetime import datetime

from celerity.coordinates import (
    GeographicCoordinate,
    convert_equatorial_to_horizontal,
)
from celerity.refraction import get_correction_to_horizontal_for_refraction
from celerity.sun import get_equatorial_coordinate

# **************************************************************************************


def get_solar_altitude(date: datetime, observer: GeographicCoordinate) -> float:
    """
    Get the current altitude of the Sun above the horizon.

    Args:
        date (datetime): The date and time for which to calculate the solar altitude.
        observer (GeographicCoordinate): The observer's geographic coordinates.

    Returns:
        float: The solar altitude (in degrees).
    """
    # Get the equatorial coordinates of the Sun for the given date:
    equatorial = get_equatorial_coordinate(date=date)

    # Convert the equatorial coordinates to horizontal coordinates:
    horizontal = convert_equatorial_to_horizontal(
        date=date,
        observer=observer,
        target=equatorial,
    )

    # Apply refraction correction to the horizontal coordinates:
    horizontal = get_correction_to_horizontal_for_refraction(
        target=horizontal,
    )

    return horizontal["alt"]


# **************************************************************************************
