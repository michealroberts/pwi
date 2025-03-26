# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest

from pwi import (
    HorizontalCalibrationParameters,
    get_horizontal_calibration_coordinates,
)
from pwi.common import NumericRange

# **************************************************************************************


class TestGetCalibrationHorizontalCoordinates(unittest.TestCase):
    def test_default_parameters_point_count(self):
        horizontal_coordinates = get_horizontal_calibration_coordinates()
        self.assertEqual(len(horizontal_coordinates), 6 * 24)

    def test_custom_sampling_pattern(self):
        params = HorizontalCalibrationParameters(
            {
                "altitude_range": NumericRange(minimum=0.0, maximum=90.0),
                "number_of_altitude_points": 3,
                "number_of_azimuth_points": 4,
            }
        )
        horizontal_coordinates = get_horizontal_calibration_coordinates(params)
        self.assertEqual(len(horizontal_coordinates), 12)

        azimuth_angles = [0.0, 90.0, 180.0, 270.0]
        ascending_altitude_values = [0.0, 45.0, 90.0]
        descending_altitude_values = list(reversed(ascending_altitude_values))

        for i, azimuth_angle in enumerate(azimuth_angles):
            altitude_values_to_use = (
                ascending_altitude_values if i % 2 == 0 else descending_altitude_values
            )
            for j, altitude_value in enumerate(altitude_values_to_use):
                index_in_list = i * 3 + j
                self.assertAlmostEqual(
                    horizontal_coordinates[index_in_list]["az"], azimuth_angle
                )
                self.assertAlmostEqual(
                    horizontal_coordinates[index_in_list]["alt"], altitude_value
                )

    def test_invalid_number_of_altitude_points_raises(self):
        for x in [0, -1]:
            with self.subTest(x=x):
                params = HorizontalCalibrationParameters(
                    {
                        "altitude_range": NumericRange(minimum=0.0, maximum=90.0),
                        "number_of_altitude_points": x,
                        "number_of_azimuth_points": 24,
                    }
                )
                with self.assertRaises(ValueError):
                    get_horizontal_calibration_coordinates(params)

    def test_invalid_number_of_azimuth_points_raises(self):
        for x in [0, -1]:
            with self.subTest(x=x):
                params = HorizontalCalibrationParameters(
                    {
                        "altitude_range": NumericRange(minimum=0.0, maximum=90.0),
                        "number_of_altitude_points": 6,
                        "number_of_azimuth_points": x,
                    }
                )
                with self.assertRaises(ValueError):
                    get_horizontal_calibration_coordinates(params)

    def test_invalid_altitude_range_raises(self):
        params = HorizontalCalibrationParameters(
            {
                "altitude_range": NumericRange(minimum=90.0, maximum=30.0),
                "number_of_altitude_points": 6,
                "number_of_azimuth_points": 24,
            }
        )
        with self.assertRaises(ValueError):
            get_horizontal_calibration_coordinates(params)

    def test_single_sample_point(self):
        params = HorizontalCalibrationParameters(
            {
                "altitude_range": NumericRange(minimum=45.0, maximum=45.0),
                "number_of_altitude_points": 1,
                "number_of_azimuth_points": 1,
            }
        )
        horizontal_coordinates = get_horizontal_calibration_coordinates(params)
        self.assertEqual(len(horizontal_coordinates), 1)
        self.assertEqual(horizontal_coordinates[0]["alt"], 45.0)
        self.assertEqual(horizontal_coordinates[0]["az"], 0.0)

    def test_single_azimuth_multiple_altitudes(self):
        params = HorizontalCalibrationParameters(
            {
                "altitude_range": NumericRange(minimum=0.0, maximum=100.0),
                "number_of_altitude_points": 5,
                "number_of_azimuth_points": 1,
            }
        )
        horizontal_coordinates = get_horizontal_calibration_coordinates(params)
        self.assertEqual(len(horizontal_coordinates), 5)
        for index_in_list, point in enumerate(horizontal_coordinates):
            self.assertEqual(point["az"], 0.0)
            self.assertAlmostEqual(point["alt"], index_in_list * 25.0)

    def test_partial_parameter_override_respected(self):
        params = HorizontalCalibrationParameters(
            {
                "altitude_range": NumericRange(minimum=30.0, maximum=90.0),
                "number_of_altitude_points": 2,
                "number_of_azimuth_points": 1,
            }
        )
        horizontal_coordinates = get_horizontal_calibration_coordinates(params)
        self.assertEqual(len(horizontal_coordinates), 2)
        self.assertEqual(horizontal_coordinates[0]["az"], 0.0)
        self.assertEqual(horizontal_coordinates[1]["az"], 0.0)
        self.assertAlmostEqual(horizontal_coordinates[0]["alt"], 30.0)
        self.assertAlmostEqual(horizontal_coordinates[1]["alt"], 90.0)

    def test_all_sample_points_unique(self):
        params = HorizontalCalibrationParameters(
            {
                "altitude_range": NumericRange(minimum=10.0, maximum=20.0),
                "number_of_altitude_points": 3,
                "number_of_azimuth_points": 3,
            }
        )
        horizontal_coordinates = get_horizontal_calibration_coordinates(params)
        seen_points_set = set(
            (point["alt"], point["az"]) for point in horizontal_coordinates
        )
        self.assertEqual(len(seen_points_set), len(horizontal_coordinates))

    def test_all_sample_points_within_bounds(self):
        params = HorizontalCalibrationParameters(
            {
                "altitude_range": NumericRange(minimum=5.0, maximum=85.0),
                "number_of_altitude_points": 5,
                "number_of_azimuth_points": 6,
            }
        )
        horizontal_coordinates = get_horizontal_calibration_coordinates(params)
        for point in horizontal_coordinates:
            self.assertGreaterEqual(point["alt"], 5.0)
            self.assertLessEqual(point["alt"], 85.0)
            self.assertGreaterEqual(point["az"], 0.0)
            self.assertLess(point["az"], 360.0)


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
