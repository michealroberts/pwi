# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest
from datetime import datetime, timezone

from pwi.axis import PlaneWaveDeviceInterfaceAxis

# **************************************************************************************


class TestPlaneWaveDeviceInterfaceAxis(unittest.TestCase):
    def test_valid_input_axis_0(self):
        raw_json = {
            "axis_number": 0,
            "mount": {
                "axis0": {
                    "is_enabled": True,
                    "rms_error_arcsec": 0.5,
                    "dist_to_target_arcsec": 1.2,
                    "servo_error_arcsec": 0.3,
                    "min_mech_position_degs": 10.0,
                    "max_mech_position_degs": 90.0,
                    "target_mech_position_degs": 45.0,
                    "position_degs": 44.9,
                    "position_timestamp": datetime(
                        2025, 3, 24, 12, 34, 56, tzinfo=timezone.utc
                    ),
                    "max_velocity_degs_per_sec": 2.5,
                    "setpoint_velocity_degs_per_sec": 2.0,
                    "measured_velocity_degs_per_sec": 1.95,
                    "acceleration_degs_per_sec_sqr": 0.05,
                    "measured_current_amps": 1.2,
                }
            },
        }

        status = PlaneWaveDeviceInterfaceAxis.model_validate(raw_json)

        self.assertTrue(status.is_enabled)
        self.assertAlmostEqual(status.rms_error, 0.5, places=5)
        self.assertAlmostEqual(status.distance_to_target, 1.2, places=5)
        self.assertAlmostEqual(status.servo_error, 0.3, places=5)
        self.assertAlmostEqual(status.minimum_mechanical_position, 10.0, places=5)
        self.assertAlmostEqual(status.maximum_mechanical_position, 90.0, places=5)
        self.assertAlmostEqual(status.target_mechanical_position, 45.0, places=5)
        self.assertAlmostEqual(status.mechanical_position, 44.9, places=5)
        self.assertEqual(
            status.last_mechanical_position_datetime,
            datetime(2025, 3, 24, 12, 34, 56, tzinfo=timezone.utc),
        )
        self.assertAlmostEqual(status.maximum_velocity, 2.5, places=5)
        self.assertAlmostEqual(status.setpoint_velocity, 2.0, places=5)
        self.assertAlmostEqual(status.measured_velocity, 1.95, places=5)
        self.assertAlmostEqual(status.acceleration, 0.05, places=5)
        self.assertAlmostEqual(status.measured_current_amps, 1.2, places=5)

    def test_valid_input_axis_1(self):
        raw_json = {
            "axis_number": 1,
            "mount": {
                "axis1": {
                    "is_enabled": "True",
                    "rms_error_arcsec": "0.5",
                    "dist_to_target_arcsec": "1.2",
                    "servo_error_arcsec": "0.3",
                    "min_mech_position_degs": "10.0",
                    "max_mech_position_degs": "90.0",
                    "target_mech_position_degs": "45.0",
                    "position_degs": "44.9",
                    "position_timestamp": datetime(
                        2025, 3, 24, 12, 34, 56, tzinfo=timezone.utc
                    ),
                    "max_velocity_degs_per_sec": "2.5",
                    "setpoint_velocity_degs_per_sec": "2.0",
                    "measured_velocity_degs_per_sec": "1.95",
                    "acceleration_degs_per_sec_sqr": "0.05",
                    "measured_current_amps": "1.2",
                }
            },
        }

        status = PlaneWaveDeviceInterfaceAxis.model_validate(raw_json)

        self.assertTrue(status.is_enabled)
        self.assertAlmostEqual(status.rms_error, 0.5, places=5)
        self.assertAlmostEqual(status.distance_to_target, 1.2, places=5)
        self.assertAlmostEqual(status.servo_error, 0.3, places=5)
        self.assertAlmostEqual(status.minimum_mechanical_position, 10.0, places=5)
        self.assertAlmostEqual(status.maximum_mechanical_position, 90.0, places=5)
        self.assertAlmostEqual(status.target_mechanical_position, 45.0, places=5)
        self.assertAlmostEqual(status.mechanical_position, 44.9, places=5)
        self.assertEqual(
            status.last_mechanical_position_datetime,
            datetime(2025, 3, 24, 12, 34, 56, tzinfo=timezone.utc),
        )
        self.assertAlmostEqual(status.maximum_velocity, 2.5, places=5)
        self.assertAlmostEqual(status.setpoint_velocity, 2.0, places=5)
        self.assertAlmostEqual(status.measured_velocity, 1.95, places=5)
        self.assertAlmostEqual(status.acceleration, 0.05, places=5)
        self.assertAlmostEqual(status.measured_current_amps, 1.2, places=5)


if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
