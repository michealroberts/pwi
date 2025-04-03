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

        telemetry = mount.get_telemetry()

        if not telemetry:
            raise RuntimeError("Failed to retrieve telemetry data.")

        print("[UTC Time]:", telemetry["utc"])

        print("[Azimuthal Telemetry]:", telemetry["azimuth"])

        print("[Altitude Telemetry]:", telemetry["polar"])
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
