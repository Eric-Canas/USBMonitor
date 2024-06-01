"""
_DarwinUSBDetector: This platform-specific implementation of the _USBDetectorBase class is designed for MacOS systems.
It provides the necessary functionality to detect USB devices connected to a MacOS system and monitor changes in their
connections. The class utilizes the ioreg command to interact with the MacOS system's device management subsystem.

Author: Eric-Canas
Date: 01-06-2024
Email: eric@ericcanas.com
Github: https://github.com/Eric-Canas
"""

from __future__ import annotations
import re
import subprocess
from warnings import warn

from ..attributes import DEVTYPE, ID_VENDOR_ID, DEVNAME, DEVICE_ATTRIBUTES
from ._constants import _DARWIN_TO_LINUX_ATTRIBUTES, _DARWIN_REGEX_ATTRIBUTES, _SECONDS_BETWEEN_CHECKS
from ._usb_detector_base import _USBDetectorBase


class _DarwinUSBDetector(_USBDetectorBase):
    def __init__(self, filter_devices: list[dict[str, str]] | tuple[dict[str, str]] | None = None):
        super(_DarwinUSBDetector, self).__init__(filter_devices=filter_devices)

    def get_available_devices(self) -> dict[str, dict[str, str]]:
        """
        Returns a dictionary of the currently available devices, where the key is the device ID and the value is a
        dictionary of the device's information.
        :return: dict[str, dict[str, str]]. The key is the device ID, the value is a dictionary of the device's
                information.
        """
        devices_info = self.__get_usb_devices()
        if self.filter_devices is not None:
            devices_info = self._apply_devices_filter(devices=devices_info)
        return devices_info

    def _monitor_changes(self, on_connect: callable | None = None, on_disconnect: callable | None = None,
                         check_every_seconds: int | float = _SECONDS_BETWEEN_CHECKS) -> None:
        """
        Monitors the USB devices. This function should ALWAYS be called from a background thread.
        :param on_connect: callable | None. The function to call when a device is added. It is expected to receive two
                arguments, the device ID and the device information. on_connect(device_id: str, device_info: dict[str, str])
        :param on_disconnect: callable | None. The function to call when a device is removed. It is expected to receive
                two arguments, the device ID and the device information. on_disconnect(device_id: str, device_info: dict[str, str])
        :param check_every_seconds: int | float. The number of seconds to wait between each check for changes in the
                USB devices. Defaults to 0.5 seconds.
        """
        while not self._stop_thread.is_set():
            self.check_changes(on_connect=on_connect, on_disconnect=on_disconnect)
            self._stop_thread.wait(check_every_seconds)

    def __get_usb_devices(self) -> dict[str, dict[str, str]]:
        """
        Retrieves the list of USB devices using the `ioreg` command.
        :return: dict[str, dict[str, str]]. A dictionary of the device information.
        """
        try:
            ioreg_output = subprocess.check_output(['ioreg', '-p', 'IOUSB', '-w0', '-l'], text=True)
        except subprocess.CalledProcessError as e:
            warn(f"Failed to retrieve USB devices information: {e}")
            return {}

        devices_info = {}
        current_device = {}
        device_id = None

        for line in ioreg_output.splitlines():
            if "+-o" in line:
                if current_device and device_id:
                    devices_info[device_id] = current_device
                current_device = {}
                device_id_match = re.search(r"\+-o\s+(.+?)\s+<", line)
                if device_id_match:
                    device_id = device_id_match.group(1)
                else:
                    device_id = None
            else:
                for attribute, darwin_attr in _DARWIN_TO_LINUX_ATTRIBUTES.items():
                    if darwin_attr in line:
                        value = line.split('=')[-1].strip().strip("}").strip('"')
                        current_device[attribute] = value

                for attribute, regex in _DARWIN_REGEX_ATTRIBUTES.items():
                    match = re.search(regex, line)
                    if match:
                        current_device[attribute] = match.group(1)

        if current_device and device_id:
            devices_info[device_id] = current_device

        # Add the device_id as the devname to the info dict
        for device_id, device_info in devices_info.items():
            device_info[DEVNAME] = device_id

        return devices_info
