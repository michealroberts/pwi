# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List

from celerity.coordinates import (
    HorizontalCoordinate,
)
from orjson import OPT_INDENT_2, dumps

from pwi import (
    BaseMountAlignmentMode,
    HorizontalCoordinateAtTime,
    PlaneWaveHTTPXClient,
    PlaneWaveMountDeviceInterface,
    PlaneWaveMountDeviceParameters,
    PlaneWaveMountDeviceTelemetry,
)

# **************************************************************************************


async def main() -> None:
    client = PlaneWaveHTTPXClient(host="100.85.19.119", port=8220)

    params: PlaneWaveMountDeviceParameters = PlaneWaveMountDeviceParameters(
        name="PlaneWave L350 Alt-Az Mount",
        description="Planewave Mount Interface (HTTP)",
        alignment=BaseMountAlignmentMode.ALT_AZ,
        latitude=33.87047,
        longitude=-118.24708,
        elevation=0.0,
        did="0",
        vid="1cbe",
        pid="0267",
    )

    mount = PlaneWaveMountDeviceInterface(
        id=0,
        params=params,
        client=client,
    )

    try:
        mount.initialise()

        print("[Connected]:", mount.is_connected())

        telemetries: List[PlaneWaveMountDeviceTelemetry] = []

        await mount.slew_to_horizontal_coordinate(
            HorizontalCoordinate(
                {
                    "alt": 45.0,
                    "az": 180.0,
                }
            )
        )

        print("[Slewing To Initial Horizontal Coordinate]: ", mount.is_slewing())

        while not mount.has_slewed_to_target():
            await asyncio.sleep(0.1)

        now = datetime.now(tz=timezone.utc)

        coordinates: List[HorizontalCoordinateAtTime] = [
            {
                "alt": 45.0,
                "az": 180.0,
                "at": now + timedelta(seconds=10),
            },
            {
                "alt": 45.0,
                "az": 183.0,
                "at": now + timedelta(seconds=11),
            },
            {
                "alt": 45.0,
                "az": 186.0,
                "at": now + timedelta(seconds=12),
            },
            {
                "alt": 45.0,
                "az": 189.0,
                "at": now + timedelta(seconds=13),
            },
            {
                "alt": 45.0,
                "az": 192.0,
                "at": now + timedelta(seconds=14),
            },
            {
                "alt": 45.0,
                "az": 195.0,
                "at": now + timedelta(seconds=15),
            },
        ]

        for horizontal in coordinates:
            mount.add_horizontal_coordinate_to_path(horizontal=horizontal)

        paths = await mount.slew_through_horizontal_coordinates_path()

        print(f"[Slewing Through Horizontal Coordinates Path]: {paths}")

        while not mount.has_slewed_to_target():
            telemetry = mount.get_telemetry()

            if telemetry is not None:
                telemetries.append(telemetry)

        print("[Slewing Completed]")

        json_bytes = dumps(telemetries, option=OPT_INDENT_2)

        print(f"[Telemetry]: {json_bytes.decode('utf-8')}")
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
