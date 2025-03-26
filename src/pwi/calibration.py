# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from typing import TypedDict

from .common import NumericRange

# **************************************************************************************


class HorizontalCalibrationParameters(TypedDict):
    """
    The parameters for a horizontal mount calibration procedure.
    """

    # The range of altitudes to calibrate (e.g., from 0° to 90°):
    altitude_range: NumericRange
    # The number of altitude points to sample between the minimum and maximum altitude:
    number_of_altitude_points: int
    # The number of azimuth points to sample from 0° up to (but not including) 360°:
    number_of_azimuth_points: int


# **************************************************************************************
