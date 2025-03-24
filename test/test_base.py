# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest
from typing import List, Optional, Tuple

from pwi import __license__, __version__
from pwi.base import BaseDeviceInterface, BaseDeviceParameters

# **************************************************************************************


def parse_semantic_version(value: str) -> Tuple[int, int, int]:
    # Split off anything after the first dash (e.g. '-rc.1', '-beta', etc.)
    version = value.split("-", 1)[0]

    # Split the main part on '.' and map them to integers
    major, minor, patch = version.split(".")

    return (int(major), int(minor), int(patch))


# **************************************************************************************


class TestBase(unittest.TestCase):
    def test_license(self) -> None:
        self.assertEqual(__license__, "MIT")

    def test_version(self):
        major, minor, patch = parse_semantic_version(__version__)
        # Assert that major, minor and patch should all be valid integers:
        self.assertIsInstance(major, int)
        self.assertIsInstance(minor, int)
        self.assertIsInstance(patch, int)


# **************************************************************************************


class DummyDeviceInterface(BaseDeviceInterface):
    """
    DummyDevice is a simple concrete implementation of BaseDeviceInterface used for testing.
    It provides fixed return values for each of the abstract methods and properties.
    """

    def __init__(self, params: Optional[BaseDeviceParameters] = None) -> None:
        super().__init__(params)
        # Initialize some attributes to verify that methods have been called.
        self.initialised = False
        self.reset_called = False
        self.connected = False

    @property
    def device_id(self) -> str:
        return self.did if self.did else ""

    @property
    def vendor_id(self) -> str:
        return self.vid if self.vid else ""

    @property
    def product_id(self) -> str:
        return self.pid if self.pid else ""

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


# **************************************************************************************


class TestDummyDevice(unittest.TestCase):
    def setUp(self) -> None:
        # Create an instance of DummyDevice with some parameters.
        params: BaseDeviceParameters = {
            "did": "ddid",
            "vid": "dvid",
            "pid": "dpid",
        }
        self.device = DummyDeviceInterface(params)

    def test_device_id_property(self) -> None:
        """Test that the device_id property exists and returns the expected value."""
        self.assertTrue(hasattr(self.device, "device_id"), "Missing device_id property")
        self.assertEqual(self.device.device_id, "ddid")

    def test_vendor_id_property(self) -> None:
        """Test that the vendor_id property exists and returns the expected value."""
        self.assertTrue(hasattr(self.device, "vendor_id"), "Missing vendor_id property")
        self.assertEqual(self.device.vendor_id, "dvid")

    def test_product_id_property(self) -> None:
        """Test that the product_id property exists and returns the expected value."""
        self.assertTrue(
            hasattr(self.device, "product_id"), "Missing product_id property"
        )
        self.assertEqual(self.device.product_id, "dpid")

    def test_initialise(self) -> None:
        """
        Test that the initialise method exists, is callable, and sets the
        initialised flag.
        """
        self.assertTrue(hasattr(self.device, "initialise"), "Missing initialise method")
        self.device.initialise()
        self.assertTrue(
            self.device.initialised, "initialise() did not set the initialised flag"
        )

    def test_reset(self) -> None:
        """Test that the reset method exists, is callable, and sets the reset flag."""
        self.assertTrue(hasattr(self.device, "reset"), "Missing reset method")
        self.device.reset()
        self.assertTrue(self.device.reset_called, "reset() did not set the reset flag")

    def test_is_connected(self) -> None:
        """Test that the is_connected method exists, is callable, and returns True."""
        self.assertTrue(
            hasattr(self.device, "is_connected"), "Missing is_connected method"
        )
        self.assertTrue(
            self.device.is_connected(), "is_connected() did not return True"
        )

    def test_is_ready(self) -> None:
        """Test that the is_ready method exists, is callable, and returns True."""
        self.assertTrue(hasattr(self.device, "is_ready"), "Missing is_ready method")
        self.assertTrue(self.device.is_ready(), "is_ready() did not return True")

    def test_get_name(self) -> None:
        """
        Test that the get_name method exists, is callable, and returns the expected
        device name.
        """
        self.assertTrue(hasattr(self.device, "get_name"), "Missing get_name method")
        self.assertEqual(self.device.get_name(), "Dummy Device")

    def test_get_description(self) -> None:
        """
        Test that the get_description method exists, is callable, and returns the
        expected description.
        """
        self.assertTrue(
            hasattr(self.device, "get_description"), "Missing get_description method"
        )
        self.assertEqual(self.device.get_description(), "Dummy description")

    def test_get_driver_version(self) -> None:
        """
        Test that the get_driver_version method exists, is callable, and returns
        the expected version tuple.
        """
        self.assertTrue(
            hasattr(self.device, "get_driver_version"),
            "Missing get_driver_version method",
        )
        self.assertEqual(self.device.get_driver_version(), (1, 0, 0))

    def test_get_firmware_version(self) -> None:
        """
        Test that the get_firmware_version method exists, is callable, and returns
        the expected version tuple.
        """
        self.assertTrue(
            hasattr(self.device, "get_firmware_version"),
            "Missing get_firmware_version method",
        )
        self.assertEqual(self.device.get_firmware_version(), (1, 0, 1))

    def test_connect(self) -> None:
        """
        Test that the connect method exists, is callable, and sets the connected flag
        to True.
        """
        self.assertTrue(hasattr(self.device, "connect"), "Missing connect method")
        self.device.connect()
        self.assertTrue(
            self.device.connected, "connect() did not set the connected flag to True"
        )

    def test_disconnect(self) -> None:
        """
        Test that the disconnect method exists, is callable, and sets the connected
        flag to False.
        """
        self.assertTrue(hasattr(self.device, "disconnect"), "Missing disconnect method")
        # First, connect the device
        self.device.connect()
        self.assertTrue(
            self.device.connected, "Device should be connected before disconnecting"
        )
        self.device.disconnect()
        self.assertFalse(
            self.device.connected,
            "disconnect() did not set the connected flag to False",
        )

    def test_get_capabilities(self) -> None:
        """
        Test that the get_capabilities method exists, is callable, and returns the
        expected list.
        """
        self.assertTrue(
            hasattr(self.device, "get_capabilities"), "Missing get_capabilities method"
        )
        self.assertEqual(
            self.device.get_capabilities(), ["capability 1", "capability 2"]
        )


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
