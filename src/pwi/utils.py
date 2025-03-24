# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from math import inf
from typing import Any, Optional

# **************************************************************************************


def is_hexadecimal(value: Optional[str]) -> bool:
    if not value:
        return False

    # Disallow leading or trailing whitespace:
    if value.strip() != value:
        return False

    try:
        int(value, 16)
        return True
    except ValueError:
        return False


# **************************************************************************************


def parse_float_safely(value: Any, default: float = inf) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# **************************************************************************************
