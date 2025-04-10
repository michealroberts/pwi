# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

import logging

from usbx import USBError, usb

# **************************************************************************************


def is_device_connected_over_usb(vid: str, pid: str) -> bool:
    """
    Checks if a USB device with the specified Vendor ID (VID) and Product ID (PID)
    is connected and communicable.

    Args:
        vid: Vendor ID (e.g., "0x046d").
        pid: Product ID (e.g., "0xc52b").

    Returns:
        bool: True if the device is connected and communicable, False otherwise.
    """
    # Attempt to convert VID to integer:
    try:
        vid_int = int(vid, 16)
    except ValueError:
        logging.error(f"Invalid VID format: {vid}. Expected hexadecimal string.")
        return False

    # Attempt to convert PID to integer:
    try:
        pid_int = int(pid, 16)
    except ValueError:
        logging.error(f"Invalid PID format: {pid}. Expected hexadecimal string.")
        return False

    devices = usb.get_devices()

    for device in devices:
        if device.vid == vid_int and device.pid == pid_int:
            try:
                return device.is_connected
            except USBError:
                # Found device, but can't open communication so return False:
                return False
            except Exception as e:
                # Handle other exceptions if needed:
                logging.error(f"Error communicating with device: {e}")
                return False

    # Device not found or not communicable:
    return False


# **************************************************************************************
