"""
USBMonitor: USBMonitor is an easy-to-use cross-platform library for USB device monitoring that simplifies
            tracking of connections, disconnections, and examination of connected device attributes on both
            Windows and Linux, freeing the user from platform-specific details or incompatibilities.

Author: Eric-Canas
Date: 24-03-2023
Email: eric@ericcanas.com
Github: https://github.com/Eric-Canas
"""

from __future__ import annotations
from .__platform_specific_detectors._constants import _SECONDS_BETWEEN_CHECKS, _THREAD_JOIN_TIMEOUT_SECONDS
from warnings import warn

import sys


class USBMonitor:
    def __init__(self, filter_devices: list[dict[str, str]] | tuple[dict[str, str]] | None = None):
        """
        Creates a new USBMonitor object. This object can be used to monitor USB devices connected to the system.

        :param filter_devices: list[dict[str, str]] | tuple[dict[str, str]] | None. A list of dictionaries containing
        the device information to filter the devices by. If None, no filtering will be done. The dictionaries
        must contain the same keys as the dictionaries returned by the `get_available_devices` method.
        For example, if you want to only monitor devices with ID_MODEL_ID = "A2B2" or "ABCD" you could pass
        filter_devices=({"ID_MODEL_ID": "A2B2"}, {"ID_MODEL_ID": "ABCD"}).
        """
        if sys.platform.startswith('linux'):
            from .__platform_specific_detectors._linux_usb_detector import _LinuxUSBDetector
            self.monitor = _LinuxUSBDetector(filter_devices=filter_devices)
        elif sys.platform.startswith('win'):
            from .__platform_specific_detectors._windows_usb_detector import _WindowsUSBDetector
            self.monitor = _WindowsUSBDetector(filter_devices=filter_devices)
        elif sys.platform.startswith('darwin'):
            from .__platform_specific_detectors._darwin_usb_detector import _DarwinUSBDetector
            self.monitor = _DarwinUSBDetector(filter_devices=filter_devices)
        else:
            raise NotImplementedError(f"Your OS is not supported: {sys.platform}")


    def get_available_devices(self) -> dict[str, dict[str, str | tuple[str, ...]]]:
        """
        Returns a dictionary of the currently available devices, where the key is the device ID and the value is a
        dictionary of the device's information. These keys IDs can be found at attributes.DEVICE_ATTRIBUTES. They
        do always correspond with the default Linux IDs (independently of the OS where the library is running).

        :return: dict[str, dict[str, str|tuple[str, ...]]]. The key is the device ID, the value is a dictionary of the device's
                information.
        """
        return self.monitor.get_available_devices()

    def check_changes(self, on_connect: callable | None = None, on_disconnect: callable | None = None,
                      update_last_check_devices: bool = True) -> None:
        """
        Checks for changes in the USB devices. If a device is removed, the `on_disconnect` function will be called
        with the device ID as the first argument and the device information as the second argument. If a device is
        added, the `on_connect` function with the same arguments.
        :param on_connect: callable | None. The function to call when a device is added. It is expected to receive
                two arguments, the device ID and the device information. on_connect(device_id: str, device_info: dict[str, str])
        :param on_disconnect: callable | None. The function to call when a device is removed. It is expected to
                receive two arguments, the device ID and the device information. on_disconnect(device_id: str, device_info: dict[str, str])
        :param update_last_check_devices: bool. Whether to update the last checked devices to the current devices
        """
        self.monitor.check_changes(on_connect=on_connect, on_disconnect=on_disconnect,
                                   update_last_check_devices=update_last_check_devices)

    def changes_from_last_check(self, update_last_check_devices: bool = True) -> tuple[dict[str, str], dict[str, str]]:
        """
        Returns a tuple of two tuples, the first containing the device IDs of the devices that were removed, the second
        containing the device IDs of the devices that were added.
        :param update_last_check_devices: bool. Whether to update the last checked devices to the current devices
        :return: tuple[dict[str, str], dict[str, str]]. The first tuple contains the information of the devices that
                were removed, the second tuple contains the information of the new devices that were added.
        """
        return self.monitor.changes_from_last_check(update_last_check_devices=update_last_check_devices)

    def start_monitoring(self, on_connect: callable|None = None, on_disconnect: callable|None = None,
                         check_every_seconds: int | float = _SECONDS_BETWEEN_CHECKS) -> None:
        """
        Starts monitoring the USB devices. This function will trigger a background thread that will check for changes
        in the USB devices every `check_every_seconds` seconds. If a device is removed, the `on_disconnect` function
        will be called with the device ID as the first argument and the device information as the second argument.
        If a device is added, the `on_connect` function with the same arguments.
        :param on_connect: callable | None. The function to call when a device is added. It is expected to receive two
                arguments, the device ID and the device information. on_connect(device_id: str, device_info: dict[str, str])
        :param on_disconnect: callable | None. The function to call when a device is removed. It is expected to receive
                two arguments, the device ID and the device information. on_disconnect(device_id: str, device_info: dict[str, str])
        :param check_every_seconds: int | float. The number of seconds to wait between each check for changes in the
                USB devices. Defaults to 0.5 seconds.
        """
        if on_connect is None and on_disconnect is None:
            warn("You are starting the monitor without any callback functions. This won't notice anything "
                 "when a device is connected or disconnected.")
        self.monitor.start_monitoring(on_connect=on_connect, on_disconnect=on_disconnect,
                                      check_every_seconds=check_every_seconds)

    def stop_monitoring(self, timeout=_THREAD_JOIN_TIMEOUT_SECONDS) -> None:
        """
        Stops monitoring the USB devices. This function will stop the background thread that was checking for changes
        in the USB devices.
        """
        self.monitor.stop_monitoring(timeout=timeout)

    # When requesting a function that does not exist, it will be redirected to the monitor
    def __getattr__(self, item):
        if hasattr(self.monitor, item):
            return getattr(self.monitor, item)
        else:
            raise AttributeError(f"USBMonitor has no attribute '{item}'")