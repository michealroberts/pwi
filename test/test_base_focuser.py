# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import unittest
from typing import List, Optional, Tuple

from pwi.base_focuser import (
    BaseFocuserDeviceInterface,
    BaseFocuserDeviceParameters,
    BaseFocuserMode,
    BaseFocuserMovingState,
)

# **************************************************************************************


class DummyFocuserDevice(BaseFocuserDeviceInterface):
    """DummyFocuserDevice provides a concrete implementation for testing."""

    _position: int = 0

    def __init__(self, params: Optional[BaseFocuserDeviceParameters] = None) -> None:
        super().__init__(params)

    def initialise(self, timeout: float = 5.0, retries: int = 3) -> None:
        self.initialised = True

    def reset(self) -> None:
        self.reset_called = True

    def is_connected(self) -> bool:
        return True

    def is_ready(self) -> bool:
        return True

    def connect(self, timeout: float = 5.0, retries: int = 3) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def get_name(self) -> str:
        return "Dummy Device"

    def get_description(self) -> str:
        return "Dummy description"

    def get_driver_version(self) -> Tuple[int, int, int]:
        return (1, 0, 0)

    def get_firmware_version(self) -> Tuple[int, int, int]:
        return (1, 0, 1)

    def get_capabilities(self) -> List[str]:
        return ["capability 1", "capability 2"]

    def enable(self) -> None:
        self._is_enabled = True

    def disable(self) -> None:
        self._is_enabled = False

    def get_position(self) -> int:
        return self._position

    def set_position(self, position: int) -> None:
        self._position = position


# **************************************************************************************


class TestDummyFocuserDevice(unittest.TestCase):
    def setUp(self) -> None:
        # Create parameters with dummy geographic values
        params: BaseFocuserDeviceParameters = BaseFocuserDeviceParameters(
            {
                "did": "",
                "vid": "",
                "pid": "",
            }
        )
        self.focuser = DummyFocuserDevice(params=params)

    def test_initialisation(self) -> None:
        # Test the initialise method
        self.focuser.initialise()
        self.assertTrue(self.focuser.initialised)

    def test_reset(self) -> None:
        # Test the reset method functionality
        self.focuser.reset()
        self.assertTrue(self.focuser.reset_called)

    def test_connect_disconnect(self) -> None:
        # Test connecting and disconnecting the device
        self.focuser.connect()
        self.assertTrue(self.focuser.connected)
        self.focuser.disconnect()
        self.assertFalse(self.focuser.connected)

    def test_get_name_and_description(self) -> None:
        # Test retrieval of name and description
        self.assertEqual(self.focuser.get_name(), "Dummy Device")
        self.assertEqual(self.focuser.get_description(), "Dummy description")

    def test_driver_and_firmware_versions(self) -> None:
        # Verify driver and firmware version numbers
        self.assertEqual(self.focuser.get_driver_version(), (1, 0, 0))
        self.assertEqual(self.focuser.get_firmware_version(), (1, 0, 1))

    def test_capabilities(self) -> None:
        # Check that the device capabilities match expectations
        self.assertEqual(
            self.focuser.get_capabilities(), ["capability 1", "capability 2"]
        )

    def test_enabled_state(self) -> None:
        # Check default enabled state, then enable and disable the focuser
        self.assertFalse(self.focuser.is_enabled())
        self.focuser.enable()
        self.assertTrue(self.focuser.is_enabled())
        self.focuser.disable()
        self.assertFalse(self.focuser.is_enabled())

    def test_moving_state(self) -> None:
        # Initially the focuser should not be moving
        self.assertFalse(self.focuser.is_moving())
        # Simulate a moving state and test the response
        self.focuser._moving_state = BaseFocuserMovingState.MOVING
        self.assertTrue(self.focuser.is_moving())
        self.focuser._moving_state = BaseFocuserMovingState.IDLE
        self.assertFalse(self.focuser.is_moving())

    def test_get_set_position(self) -> None:
        # Verify the default focuser position and then set a new one
        self.assertEqual(self.focuser.get_position(), 0)
        expected_position = 1234
        self.focuser.set_position(expected_position)
        self.assertEqual(self.focuser.get_position(), expected_position)

    def test_default_mode(self) -> None:
        # Verify that the default focuser mode is ABSOLUTE
        self.assertEqual(self.focuser.get_mode(), BaseFocuserMode.ABSOLUTE)

    def test_default_id(self) -> None:
        # Verify that the default device ID is 0
        self.assertEqual(self.focuser._id, 0)


# **************************************************************************************

if __name__ == "__main__":
    unittest.main()

# **************************************************************************************
