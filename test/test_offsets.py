# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest

from pwi import PlaneWaveDeviceInterfaceOffsets
from pwi.units import (
    convert_arcseconds_to_degrees,  # Used here to compute expected values
)

# **************************************************************************************


class TestPlaneWaveDeviceInterfaceOffsets(unittest.TestCase):
    def test_offset_parsing(self):
        raw_json = {
            "mount": {
                "offsets": {
                    "ra_arcsec": {
                        "total": 0.5,
                        "rate": 0.1,
                        "gradual_offset_progress": 0.2,
                    },
                    "dec_arcsec": {
                        "total": 1.2,
                        "rate": 0.3,
                        "gradual_offset_progress": 0.4,
                    },
                    "axis0_arcsec": {
                        "total": 2.5,
                        "rate": 0.5,
                        "gradual_offset_progress": 0.6,
                    },
                    "axis1_arcsec": {
                        "total": 3.8,
                        "rate": 0.7,
                        "gradual_offset_progress": 0.8,
                    },
                    "path_arcsec": {
                        "total": 4.1,
                        "rate": 0.9,
                        "gradual_offset_progress": 1.0,
                    },
                    "transverse_arcsec": {
                        "total": 5.4,
                        "rate": 1.1,
                        "gradual_offset_progress": 1.2,
                    },
                },
            },
        }

        offsets = PlaneWaveDeviceInterfaceOffsets.model_validate(raw_json)

        self.assertIsNotNone(offsets.ra)
        expected_ra_offset = convert_arcseconds_to_degrees(0.5)
        expected_ra_rate = convert_arcseconds_to_degrees(0.1)
        self.assertAlmostEqual(offsets.ra.offset, expected_ra_offset, places=6)
        self.assertAlmostEqual(offsets.ra.rate, expected_ra_rate, places=6)
        self.assertAlmostEqual(offsets.ra.gradual_progress_adjustment, 0.2, places=6)

        self.assertIsNotNone(offsets.dec)
        expected_dec_offset = convert_arcseconds_to_degrees(1.2)
        expected_dec_rate = convert_arcseconds_to_degrees(0.3)
        self.assertAlmostEqual(offsets.dec.offset, expected_dec_offset, places=6)
        self.assertAlmostEqual(offsets.dec.rate, expected_dec_rate, places=6)
        self.assertAlmostEqual(offsets.dec.gradual_progress_adjustment, 0.4, places=6)

        self.assertIsNotNone(offsets.axis0)
        expected_axis0_offset = convert_arcseconds_to_degrees(2.5)
        expected_axis0_rate = convert_arcseconds_to_degrees(0.5)
        self.assertAlmostEqual(offsets.axis0.offset, expected_axis0_offset, places=6)
        self.assertAlmostEqual(offsets.axis0.rate, expected_axis0_rate, places=6)
        self.assertAlmostEqual(offsets.axis0.gradual_progress_adjustment, 0.6, places=6)

        self.assertIsNotNone(offsets.axis1)
        expected_axis1_offset = convert_arcseconds_to_degrees(3.8)
        expected_axis1_rate = convert_arcseconds_to_degrees(0.7)
        self.assertAlmostEqual(offsets.axis1.offset, expected_axis1_offset, places=6)
        self.assertAlmostEqual(offsets.axis1.rate, expected_axis1_rate, places=6)
        self.assertAlmostEqual(offsets.axis1.gradual_progress_adjustment, 0.8, places=6)

        self.assertIsNotNone(offsets.path)
        expected_path_offset = convert_arcseconds_to_degrees(4.1)
        expected_path_rate = convert_arcseconds_to_degrees(0.9)
        self.assertAlmostEqual(offsets.path.offset, expected_path_offset, places=6)
        self.assertAlmostEqual(offsets.path.rate, expected_path_rate, places=6)
        self.assertAlmostEqual(offsets.path.gradual_progress_adjustment, 1.0, places=6)

        self.assertIsNotNone(offsets.transverse)
        expected_transverse_offset = convert_arcseconds_to_degrees(5.4)
        expected_transverse_rate = convert_arcseconds_to_degrees(1.1)
        self.assertAlmostEqual(
            offsets.transverse.offset, expected_transverse_offset, places=6
        )
        self.assertAlmostEqual(
            offsets.transverse.rate, expected_transverse_rate, places=6
        )
        self.assertAlmostEqual(
            offsets.transverse.gradual_progress_adjustment, 1.2, places=6
        )

    def test_offset_missing_keys(self):
        raw_json = {"mount": {"offsets": {}}}
        offsets = PlaneWaveDeviceInterfaceOffsets.model_validate(raw_json)
        self.assertIsNone(offsets.ra)
        self.assertIsNone(offsets.dec)
        self.assertIsNone(offsets.axis0)
        self.assertIsNone(offsets.axis1)
        self.assertIsNone(offsets.path)
        self.assertIsNone(offsets.transverse)


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
