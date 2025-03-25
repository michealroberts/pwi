# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest
from typing import List, Optional, Tuple

from celerity.coordinates import EquatorialCoordinate, HorizontalCoordinate

from pwi import (
    BaseMountDeviceInterface,
    BaseMountDeviceParameters,
)

# **************************************************************************************


class DummyMountDevice(BaseMountDeviceInterface):
    """DummyMountDevice provides a concrete implementation for testing."""

    def __init__(self, params: Optional[BaseMountDeviceParameters] = None) -> None:
        super().__init__(params)

    def initialise(self, timeout: float = 5.0, retries: int = 3) -> None:
        self.initialised = True

    def reset(self) -> None:
        self.reset_called = True

    def is_connected(self) -> bool:
        return True

    def is_ready(self) -> bool:
        return True

    def get_name(self) -> str:
        return "Dummy Device"

    def get_description(self) -> str:
        return "Dummy description"

    def get_driver_version(self) -> Tuple[int, int, int]:
        return (1, 0, 0)

    def get_firmware_version(self) -> Tuple[int, int, int]:
        return (1, 0, 1)

    def connect(self, timeout: float = 5.0, retries: int = 3) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def get_capabilities(self) -> List[str]:
        return ["capability 1", "capability 2"]

    def can_find_home(self) -> bool:
        return True

    def is_home(self) -> bool:
        return True

    async def find_home(self) -> None:
        pass

    def get_right_ascension(self) -> float:
        return 180.0

    def get_declination(self) -> float:
        return 45.0

    def get_altitude(self) -> float:
        return 60.0

    def get_azimuth(self) -> float:
        return 120.0

    def get_slew_rate(self) -> float:
        return 1.5

    def get_slew_settle_time(self) -> float:
        return 2.0

    def is_slewing(self) -> bool:
        return False

    def does_refraction(self) -> bool:
        return True

    async def slew_to_equatorial_coordinate(
        self, equatorial: EquatorialCoordinate
    ) -> bool:
        return True

    async def slew_to_horizontal_coordinate(
        self, horizontal: HorizontalCoordinate
    ) -> bool:
        return True

    async def slew_to_topocentric_coordinate(
        self, topocentric: HorizontalCoordinate
    ) -> bool:
        return True

    def abort_slew(self) -> None:
        pass

    def is_tracking(self) -> bool:
        return True

    async def sync_to_equatorial_coordinate(
        self, equatorial: EquatorialCoordinate
    ) -> None:
        pass

    async def sync_to_horizontal_coordinate(
        self, horizontal: HorizontalCoordinate
    ) -> None:
        pass

    async def sync_to_topocentric_coordinates(
        self, topocentric: HorizontalCoordinate
    ) -> None:
        pass

    async def sync_to_tle(self, tle: str) -> None:
        pass

    def get_tracking_rate(self) -> float:
        return 1.0

    def set_tracking_rate(self, rate: float) -> None:
        pass

    def abort_tracking(self) -> None:
        pass


# **************************************************************************************


class TestDummyMountDevice(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        params: BaseMountDeviceParameters = BaseMountDeviceParameters(
            {
                "did": "",
                "vid": "",
                "pid": "",
                "latitude": 51.5,
                "longitude": -0.12,
                "elevation": 100.0,
            }
        )
        self.mount = DummyMountDevice(params=params)

    def test_initialisation(self) -> None:
        self.assertEqual(self.mount._latitude, 51.5)
        self.assertEqual(self.mount._longitude, -0.12)
        self.assertEqual(self.mount._elevation, 100.0)

    def test_can_find_home(self) -> None:
        self.assertTrue(self.mount.can_find_home())

    def test_is_home(self) -> None:
        self.assertTrue(self.mount.is_home())

    async def test_find_home(self) -> None:
        await self.mount.find_home()

    def test_coordinates(self) -> None:
        self.assertEqual(self.mount.get_right_ascension(), 180.0)
        self.assertEqual(self.mount.get_declination(), 45.0)
        self.assertEqual(self.mount.get_altitude(), 60.0)
        self.assertEqual(self.mount.get_azimuth(), 120.0)

    def test_slew_properties(self) -> None:
        self.assertEqual(self.mount.get_slew_rate(), 1.5)
        self.assertEqual(self.mount.get_slew_settle_time(), 2.0)
        self.assertFalse(self.mount.is_slewing())

    async def test_slew_to_equatorial(self) -> None:
        target = EquatorialCoordinate(ra=10.0, dec=-10.0)
        result = await self.mount.slew_to_equatorial_coordinate(target)
        self.assertTrue(result)

    async def test_slew_to_horizontal(self) -> None:
        target = HorizontalCoordinate(alt=30.0, az=90.0)
        result = await self.mount.slew_to_horizontal_coordinate(target)
        self.assertTrue(result)

    def test_tracking_state(self) -> None:
        self.assertTrue(self.mount.is_tracking())

    def test_does_refraction(self) -> None:
        self.assertTrue(self.mount.does_refraction())

    async def test_sync_to_equatorial(self) -> None:
        target = EquatorialCoordinate(ra=15.0, dec=45.0)
        await self.mount.sync_to_equatorial_coordinate(target)

    def test_tracking_rate(self) -> None:
        self.assertEqual(self.mount.get_tracking_rate(), 1.0)


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
