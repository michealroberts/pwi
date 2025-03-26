# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest

from pwi.status import PlaneWaveDeviceInterfaceStatus

# **************************************************************************************


class TestPlaneWaveDeviceInterfaceStatus(unittest.TestCase):
    def test_planewave_status_parsing(self):
        raw_json = {
            "mount": {
                "is_connected": "true",
                "is_slewing": "false",
                "is_tracking": "true",
                "julian_date": "2459876.456",
                "ra_j2000_hours": 12.34,
                "dec_j2000_degs": -22.22,
                "ra_apparent_hours": 12.89,
                "dec_apparent_degs": -21.0,
                "target_ra_j2000_hours": 13.0,
                "target_dec_j2000_degs": -20.0,
                "target_ra_apparent_hours": 13.5,
                "target_dec_apparent_degs": -19.5,
                "altitude_degs": 45.5,
                "azimuth_degs": 180.0,
            },
            "focuser": {},
            "rotator": {},
        }
        status = PlaneWaveDeviceInterfaceStatus.model_validate(raw_json)

        self.assertTrue(status.is_connected)
        self.assertFalse(status.is_slewing)
        self.assertTrue(status.is_tracking)
        self.assertAlmostEqual(status.JD, 2459876.456, places=6)

        self.assertIsNotNone(status.j2000_equatorial_coordinate)
        self.assertAlmostEqual(
            status.j2000_equatorial_coordinate["ra"], 185.1, places=4
        )
        self.assertAlmostEqual(
            status.j2000_equatorial_coordinate["dec"], -22.22, places=4
        )

        self.assertIsNotNone(status.apparent_equatorial_coordinate)
        self.assertAlmostEqual(
            status.apparent_equatorial_coordinate["ra"], 193.35, places=4
        )
        self.assertAlmostEqual(
            status.apparent_equatorial_coordinate["dec"], -21.0, places=4
        )

        self.assertIsNotNone(status.target_j2000_equatorial_coordinate)
        self.assertAlmostEqual(
            status.target_j2000_equatorial_coordinate["ra"], 195.0, places=4
        )
        self.assertAlmostEqual(
            status.target_j2000_equatorial_coordinate["dec"], -20.0, places=4
        )

        self.assertIsNotNone(status.target_apparent_equatorial_coordinate)
        self.assertAlmostEqual(
            status.target_apparent_equatorial_coordinate["ra"], 202.5, places=4
        )
        self.assertAlmostEqual(
            status.target_apparent_equatorial_coordinate["dec"], -19.5, places=4
        )

        self.assertIsNotNone(status.horizontal_coordinate)
        self.assertAlmostEqual(status.horizontal_coordinate["alt"], 45.5, places=3)
        self.assertAlmostEqual(status.horizontal_coordinate["az"], 180.0, places=3)

    def test_planewave_status_missing_keys(self):
        raw_json = {"mount": {}}
        status = PlaneWaveDeviceInterfaceStatus.model_validate(raw_json)

        self.assertFalse(status.is_connected)
        self.assertFalse(status.is_slewing)
        self.assertFalse(status.is_tracking)
        self.assertIsNone(status.JD)
        self.assertIsNone(status.j2000_equatorial_coordinate)
        self.assertIsNone(status.horizontal_coordinate)


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
