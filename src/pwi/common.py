# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from typing import TypedDict, Union

# **************************************************************************************


class NumericRange(TypedDict):
    """
    A class to store the parameters for a range.
    """

    minimum: Union[int, float]
    maximum: Union[int, float]


# **************************************************************************************
