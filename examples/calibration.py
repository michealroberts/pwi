# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import asyncio

from pwi import get_horizontal_calibration_coordinates

# **************************************************************************************


async def main() -> None:
    horizontal_coordinates = get_horizontal_calibration_coordinates(
        params={
            "altitude_range": {"minimum": 20.0, "maximum": 90.0},
        }
    )

    print(horizontal_coordinates)


# **************************************************************************************

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user via KeyboardInterrupt.")
    except Exception as e:
        print(f"An unexpected exception occurred: {e}")

# **************************************************************************************
