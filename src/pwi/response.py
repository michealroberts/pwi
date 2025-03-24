# **************************************************************************************

# @package        @lumispace/sunrise
# @license        Copyright © 2025 Lumi.Space

# **************************************************************************************

import re
from typing import (
    Any,
    Dict,
    List,
    Union,
)

# **************************************************************************************


class ResponsePlanTextParserToJSON:
    """
    A parser that converts a custom text-based response plan into a nested dictionary.
    It supports dot-delimited keys for nesting and array-like keys with indices.
    """

    def __init__(self, raw: Union[bytes, str]) -> None:
        """
        Initialize the parser with raw data.

        Args:
            raw (Union[bytes, str]): The raw data to parse. It can be provided as bytes or as a string.
        """
        # If the input is in bytes, decode it into a string using UTF-8:
        if isinstance(raw, bytes):
            self.data: str = raw.decode("utf-8")
        else:
            self.data = raw

    def parse(self) -> Dict[str, Any]:
        """
        Parse the raw data into a nested dictionary.

        This method:
          - Splits the raw text into individual lines.
          - Ignores empty or malformed lines (lines without an "=").
          - Splits each valid line into a key and a value at the first "=" encountered.
          - Trims the key and value, converts the value to an appropriate type,
            and inserts it into a nested dictionary using the key's structure.

        Returns:
            Dict[str, Any]: A nested dictionary representing the parsed data.
        """
        # Initialize an empty dictionary to store the results:
        result: Dict[str, Any] = {}

        # Process each line from the raw data:
        for line in self.data.splitlines():
            # Skip any empty lines (after stripping whitespace):
            if not line.strip():
                continue

            # Skip lines that do not have an '=' sign (considered malformed):
            if "=" not in line:
                continue

            # Split the line into a key and value at the first '=' character:
            key, value = line.split("=", 1)

            # Clean and convert the value, then insert the key/value pair into the nested dictionary:
            self._insert_into_dict(
                result,
                key.strip(),
                self._convert_value(value.strip()),
            )

        return result

    def _convert_value(self, value: str) -> Union[bool, int, float, str]:
        """
        Convert a string value to its appropriate type (bool, int, or float).

        The conversion steps are:
          - Convert "true"/"false" (case insensitive) to boolean True/False.
          - Attempt to convert the string to a float; if it represents an integer (e.g., "5.0"),
            return it as an int.
          - If the conversion fails, return the original string.

        Args:
            value (str): The string value to convert.

        Returns:
            Union[bool, int, float, str]: The value in its appropriate type.
        """
        # Check for boolean values in a case-insensitive manner:
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False

        # Try converting the string to a numeric value:
        try:
            numeric: float = float(value)
            if numeric.is_integer():
                return int(numeric)
            return numeric
        except ValueError:
            # If conversion to a number fails, return the original string:
            return value

    def _insert_into_dict(
        self, container: Dict[str, Any], key: str, value: Any
    ) -> None:
        """
        Insert the key/value pair into a dictionary, supporting nested keys and array indices.

        This method supports:
          - Dot-delimited keys for creating nested dictionaries.
          - Keys with array indices (e.g., "settings[0]") by creating lists and extending them as needed.

        Args:
            container (Dict[str, Any]): The dictionary to insert the key/value pair into.
            key (str): The key string, which may include dot notation and array indices.
            value (Any): The value to insert into the dictionary.
        """
        # Split the key by '.' to support nested structure:
        parts: List[str] = key.split(".")

        # Start with the top-level container as the current dictionary:
        current: Dict[str, Any] = container

        # Iterate through each part of the split key:
        for i, part in enumerate(parts):
            # Check if the current part includes an array index using a regular expression:
            array_match = re.match(r"(.+)\[(\d+)\]", part)

            if array_match:
                # Extract the base key (e.g., "settings") and the index (e.g., 0):
                base_key: str = array_match.group(1)
                index: int = int(array_match.group(2))

                # If the base key is not present or is not a list, initialize it as a list:
                if base_key not in current or not isinstance(current[base_key], list):
                    current[base_key] = []

                # Ensure the list is long enough to include the specified index:
                while len(current[base_key]) <= index:
                    current[base_key].append(
                        {}
                    )  # Append an empty dictionary as a placeholder:

                # If this is the last part of the key, assign the value directly:
                if i == len(parts) - 1:
                    current[base_key][index] = value
                else:
                    # If the next level is not a dictionary, initialize it as one:
                    if not isinstance(current[base_key][index], dict):
                        current[base_key][index] = {}
                    # Move deeper into the nested structure:
                    current = current[base_key][index]
            else:
                # For a simple key (without an array index):
                if i == len(parts) - 1:
                    # If this is the final key part, insert the value:
                    current[part] = value
                else:
                    # If the key does not exist or is not a dictionary, initialize it as an empty dictionary:
                    if part not in current or not isinstance(current[part], dict):
                        current[part] = {}
                    # Move into the nested dictionary for further insertion:
                    current = current[part]


# **************************************************************************************
