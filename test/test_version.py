# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest

from pwi.version import PlanewaveDeviceInterfaceVersion

# **************************************************************************************


class TestPlanewaveDeviceInterfaceVersion(unittest.TestCase):
    def test_list_input(self):
        # Test with a list input for version.
        data = {"pwi4": {"version": [1, 2, 3]}}
        obj = PlanewaveDeviceInterfaceVersion.model_validate(data)
        self.assertEqual(obj.version, (1, 2, 3))

    def test_string_input(self):
        # Test with a version provided as a string.
        data = {"pwi4": {"version": "1.2.3"}}
        obj = PlanewaveDeviceInterfaceVersion.model_validate(data)
        self.assertEqual(obj.version, (1, 2, 3))

    def test_version_field_override(self):
        # When "version_field" is present it should override "version".
        data = {"pwi4": {"version": [1, 2, 3], "version_field": "4.5.6"}}
        obj = PlanewaveDeviceInterfaceVersion.model_validate(data)
        self.assertEqual(obj.version, (4, 5, 6))

    def test_tuple_input_padding(self):
        # Test with a tuple that has fewer than three items.
        data = {"pwi4": {"version": (7,)}}
        obj = PlanewaveDeviceInterfaceVersion.model_validate(data)
        # Expected: (7, 0, 0) after padding.
        self.assertEqual(obj.version, (7, 0, 0))

    def test_string_with_four_parts(self):
        # Even if four parts are provided, only the first three should be returned.
        data = {"pwi4": {"version": "7.8.9.10"}}
        obj = PlanewaveDeviceInterfaceVersion.model_validate(data)
        self.assertEqual(obj.version, (7, 8, 9))

    def test_invalid_version(self):
        # A non-numeric string should raise a ValueError.
        data = {"pwi4": {"version": "abc"}}
        with self.assertRaises(ValueError):
            PlanewaveDeviceInterfaceVersion.model_validate(data)

    def test_missing_pwi4(self):
        # Without a 'pwi4' key the model validator assigns "<unknown>" which cannot be parsed.
        data = {}
        with self.assertRaises(ValueError):
            PlanewaveDeviceInterfaceVersion.model_validate(data)


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
