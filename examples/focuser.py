# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import asyncio

from pwi import (
    PlaneWaveFocuserDeviceInterface,
    PlaneWaveFocuserDeviceParameters,
    PlaneWaveHTTPXClient,
)

# **************************************************************************************


async def main() -> None:
    client = PlaneWaveHTTPXClient(host="localhost", port=8220)

    params: PlaneWaveFocuserDeviceParameters = PlaneWaveFocuserDeviceParameters(
        name="PlaneWave L350 Alt-Az Focuser",
        description="Planewave Focuser Interface (HTTP)",
        did="0",
        vid="",
        pid="",
    )

    focuser = PlaneWaveFocuserDeviceInterface(
        id=0,
        params=params,
        client=client,
    )

    try:
        focuser.initialise()

        status = focuser.get_status()

        print(status)
    except asyncio.CancelledError:
        print("Operation was cancelled.")
    except KeyboardInterrupt:
        print("Keyboard interrupt received during execution. Exiting gracefully.")
    finally:
        focuser.disconnect()


# **************************************************************************************

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user via KeyboardInterrupt.")
    except Exception as e:
        print(f"An unexpected exception occurred: {e}")

# **************************************************************************************
