# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest

from pwi.utils import is_hexadecimal

# **************************************************************************************


class TestIsHexadecimal(unittest.TestCase):
    def test_none_input(self) -> None:
        """A None value should be rejected."""
        self.assertFalse(is_hexadecimal(None), msg="None input should return False.")

    def test_empty_string(self) -> None:
        """An empty string should be rejected."""
        self.assertFalse(is_hexadecimal(""), msg="Empty string should return False.")

    def test_valid_hex_alphanumeric(self) -> None:
        """Valid hexadecimal strings composed solely of alphanumeric digits should be accepted."""
        valid_hexadecimal = {
            "1A3F": True,
            "abcdef": True,
            "ABCDEF": True,
            "0": True,
            "1234567890ABCDEF": True,
        }

        for input_value, expected in valid_hexadecimal.items():
            with self.subTest(input_val=input_value):
                self.assertEqual(
                    is_hexadecimal(input_value),
                    expected,
                    msg=f"Input '{input_value}' should be recognized as a valid hexadecimal string.",
                )

    def test_invalid_hex_with_non_hex_alphanumerics(self) -> None:
        """Hex strings containing alphanumeric characters outside 0-9 and A-F/a-f should be rejected."""
        invalid_hexadecimal = {
            "GHIJK": False,  # contains letters beyond F
            "123Z": False,  # contains a non-hex letter
        }
        for input_value, expected in invalid_hexadecimal.items():
            with self.subTest(input_val=input_value):
                self.assertEqual(
                    is_hexadecimal(input_value),
                    expected,
                    msg=f"Input '{input_value}' should be rejected as it contains non-hexadecimal characters.",
                )

    def test_valid_hex_with_prefix(self) -> None:
        """Hex strings with a '0x' prefix should be accepted."""
        self.assertTrue(
            is_hexadecimal("0x1A3F"),
            msg="Input '0x1A3F' should be accepted because the '0x' prefix is allowed.",
        )

    def test_invalid_hex_with_special_characters(self) -> None:
        """Hex strings containing special characters such as a dot should be rejected."""
        self.assertFalse(
            is_hexadecimal("12.34"),
            msg="Input '12.34' should be rejected due to the presence of a dot.",
        )

    def test_invalid_hex_due_to_whitespace(self) -> None:
        """Hex strings with leading, trailing, or only whitespace should be rejected."""
        whitespace_cases = {
            " ": False,
            " 1A3F": False,
            "1A3F ": False,
            "\t1A3F\n": False,
        }
        for input_value, expected in whitespace_cases.items():
            with self.subTest(input_val=repr(input_value)):
                self.assertEqual(
                    is_hexadecimal(input_value),
                    expected,
                    msg=f"Input {repr(input_value)} should be rejected due to extra whitespace.",
                )


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
