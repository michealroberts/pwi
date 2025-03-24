# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest
from math import inf

from pwi.site import PlanewaveDeviceInterfaceSite

# **************************************************************************************


class TestPlanewaveDeviceInterfaceSite(unittest.TestCase):
    def test_valid_input(self):
        raw_json = {
            "site": {
                "latitude_degs": 12.34,
                "longitude_degs": 56.78,
                "height_meters": 100.0,
                "lmst_hours": 23.45,
            }
        }
        status = PlanewaveDeviceInterfaceSite.model_validate(raw_json)
        self.assertAlmostEqual(status.latitude, 12.34, places=5)
        self.assertAlmostEqual(status.longitude, 56.78, places=5)
        self.assertAlmostEqual(status.elevation, 100.0, places=5)
        self.assertAlmostEqual(status.lmst, 23.45, places=5)

    def test_valid_input_strings(self):
        raw_json = {
            "site": {
                "latitude_degs": "12.34",
                "longitude_degs": "56.78",
                "height_meters": "100.0",
                "lmst_hours": "23.45",
            }
        }
        status = PlanewaveDeviceInterfaceSite.model_validate(raw_json)
        self.assertAlmostEqual(status.latitude, 12.34, places=5)
        self.assertAlmostEqual(status.longitude, 56.78, places=5)
        self.assertAlmostEqual(status.elevation, 100.0, places=5)
        self.assertAlmostEqual(status.lmst, 23.45, places=5)

    def test_missing_keys(self):
        raw_json = {"site": {}}
        status = PlanewaveDeviceInterfaceSite.model_validate(raw_json)
        self.assertEqual(status.latitude, inf)
        self.assertEqual(status.longitude, inf)
        self.assertEqual(status.elevation, inf)
        self.assertEqual(status.lmst, inf)

    def test_invalid_input(self):
        raw_json = {
            "site": {
                "latitude_degs": "invalid",
                "longitude_degs": "invalid",
                "height_meters": "invalid",
                "lmst_hours": "invalid",
            }
        }
        status = PlanewaveDeviceInterfaceSite.model_validate(raw_json)
        self.assertEqual(status.latitude, inf)
        self.assertEqual(status.longitude, inf)
        self.assertEqual(status.elevation, inf)
        self.assertEqual(status.lmst, inf)


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
