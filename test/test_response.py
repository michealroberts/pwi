# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest

from pwi.response import (
    ResponsePlanTextParserToJSON,
)

# **************************************************************************************


class TestResponsePlanTextParserToJSON(unittest.TestCase):
    def test_basic_parsing(self):
        # Test that basic key-value pairs are parsed correctly:
        raw = b"key1=value1\nkey2=42\nkey3=true\n"
        parser = ResponsePlanTextParserToJSON(raw)
        result = parser.parse()
        expected = {"key1": "value1", "key2": 42, "key3": True}
        self.assertEqual(result, expected)

    def test_nested_parsing(self):
        # Test that dot-delimited keys create nested dictionaries:
        raw = b"parent.child=hello\nparent.child2=world\n"
        parser = ResponsePlanTextParserToJSON(raw)
        result = parser.parse()
        expected = {"parent": {"child": "hello", "child2": "world"}}
        self.assertEqual(result, expected)

    def test_array_parsing(self):
        # Test that keys with array indices produce lists with the correct values:
        raw = b"array[0]=first\narray[1]=second\n"
        parser = ResponsePlanTextParserToJSON(raw)
        result = parser.parse()
        expected = {"array": ["first", "second"]}
        self.assertEqual(result, expected)

    def test_mixed_parsing(self):
        # Test a combination of nested keys and array indices:
        raw = b"a.b[0]=1\na.b[1]=2\na.c=3\n"
        parser = ResponsePlanTextParserToJSON(raw)
        result = parser.parse()
        expected = {"a": {"b": [1, 2], "c": 3}}
        self.assertEqual(result, expected)

    def test_incorrect_lines(self):
        # Test that lines without '=' and empty lines are ignored:
        raw = b"\nincorrect line\nkey=value\n"
        parser = ResponsePlanTextParserToJSON(raw)
        result = parser.parse()
        expected = {"key": "value"}
        self.assertEqual(result, expected)


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
