# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from typing import Optional

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
