# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import asyncio

from pwi import (
    BaseMountAlignmentMode,
    PlaneWaveHTTPXClient,
    PlaneWaveMountDeviceInterface,
    PlaneWaveMountDeviceParameters,
)

# **************************************************************************************


async def main() -> None:
    client = PlaneWaveHTTPXClient(host="localhost", port=8220)

    params: PlaneWaveMountDeviceParameters = PlaneWaveMountDeviceParameters(
        name="PlaneWave L350 Alt-Az Mount",
        description="Planewave Mount Interface (HTTP)",
        alignment=BaseMountAlignmentMode.ALT_AZ,
        latitude=33.87047,
        longitude=-118.24708,
        elevation=0.0,
        did="0",
        vid="",
        pid="",
    )

    mount = PlaneWaveMountDeviceInterface(
        id=0,
        params=params,
        client=client,
    )

    try:
        mount.initialise()

        print("[Connected]:", mount.is_connected())

        tle_string = """
        0 STARLINK-5833
        1 55773U 23028AJ  23067.83334491 -.01005600  31449-3 -24643-2 0  9994
        2 55773  69.9999 141.6053 0033105 165.0362 252.1405 15.94888459  1455
        """

        tle = "\n".join(line.strip() for line in tle_string.strip().splitlines())

        mount.slew_to_and_follow_tle(tle=tle)

        while True:
            topocentric = mount.get_topocentric_coordinate()

            print(topocentric)

            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Operation was cancelled.")
    except KeyboardInterrupt:
        print("Keyboard interrupt received during execution. Exiting gracefully.")
    finally:
        mount.disconnect()


# **************************************************************************************

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user via KeyboardInterrupt.")
    except Exception as e:
        print(f"An unexpected exception occurred: {e}")

# **************************************************************************************
