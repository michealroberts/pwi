# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import asyncio

from celerity.coordinates import (
    EquatorialCoordinate,
    HorizontalCoordinate,
)

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

        status = mount.get_status()

        print(status)

        site = mount.get_site()

        print(site)

        print("[Connected]:", mount.is_connected())

        version = mount.get_driver_version()

        print("[Driver Version]:", version)

        mode = mount.get_alignment_mode()

        print("[Alignment Mode]:", mode)

        tracking = mount.get_tracking_mode()

        print("[Tracking Mode]:", tracking)

        is_ready = mount.is_ready()

        print("[Is Ready]:", is_ready)

        # await mount.find_home()

        await mount.sync_to_horizontal_coordinate(
            HorizontalCoordinate(
                {
                    "alt": 45.0,
                    "az": 180.0,
                }
            )
        )

        offsets = mount.get_offsets()

        print("[Offsets]:", offsets)

        while not mount.has_slewed_to_target():
            await asyncio.sleep(0.1)

        ra = mount.get_right_ascension()

        dec = mount.get_declination()

        print("[RA]:", ra, "[DEC]:", dec)

        alt = mount.get_altitude()

        az = mount.get_azimuth()

        print("[Altitude]:", alt, "[Azimuth]:", az)

        mount.model_load(filename="active.model")

        mount.model_add_point(EquatorialCoordinate({"ra": 0.0, "dec": 0.0}))

        mount.model_save(filename="active.model")

        mount.model_enable_point([0])

        mount.model_disable_point([0])

        mount.model_delete_point([0])

        mount.model_add_point(EquatorialCoordinate({"ra": 0.0, "dec": 0.0}))

        mount.model_clear_points()

        mount.set_park(
            HorizontalCoordinate(
                {
                    "az": 0.0,
                    "alt": 15.0,
                }
            )
        )

        mount.find_park()
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
