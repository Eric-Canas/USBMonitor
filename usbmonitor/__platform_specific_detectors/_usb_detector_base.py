"""
_USBDetectorBase: This abstract base class provides the core functionality for monitoring USB devices on different
platforms. It defines the required methods and attributes, as well as common functionality for checking device changes,
starting and stopping the monitoring process, and maintaining the state of the monitoring thread. The _USBDetectorBase
class is intended to be subclassed by platform-specific implementations to provide the necessary support for USB
device monitoring.

Author: Eric-Canas
Date: 27-03-2023
Email: eric@ericcanas.com
Github: https://github.com/Eric-Canas
"""
from __future__ import annotations

import threading
from warnings import warn
from abc import ABC, abstractmethod

from usbmonitor.__platform_specific_detectors._constants import _SECONDS_BETWEEN_CHECKS

class _USBDetectorBase(ABC):
    def __init__(self):
        self._thread = None
        self._stop_thread = threading.Event()
        self.lock = threading.Lock()

        self.on_start_devices = self.get_current_available_devices()
        self.last_check_devices = self.on_start_devices.copy()

    def changes_from_last_check(self, update_last_check_devices: bool = True) -> tuple[dict[str, str], dict[str, str]]:
        """
        Returns a tuple of two tuples, the first containing the device IDs of the devices that were removed, the second
        containing the device IDs of the devices that were added.
        :param update_last_check_devices: bool. Whether to update the last checked devices to the current devices
        :return: tuple[dict[str, str], dict[str, str]]. The first tuple contains the information of the devices that
                were removed, the second tuple contains the information of the new devices that were added.
        """
        current_devices, prev_devices = self.get_current_available_devices(), self.last_check_devices
        # Get the difference between the current devices and the previous ones
        removed_devices = {_id: _info for _id, _info in prev_devices.items() if _id not in current_devices}
        added_devices = {_id: _info for _id, _info in current_devices.items() if _id not in prev_devices}
        # Update the last checked devices to the current devices if requested
        if update_last_check_devices:
            self.last_check_devices = current_devices.copy()
        return removed_devices, added_devices

    @abstractmethod
    def get_current_available_devices(self) -> dict[str, dict[str, str|tuple[str, ...]]]:
        """
        Returns a dictionary of the currently available devices, where the key is the device ID and the value is a
        dictionary of the device's information.
        :return: dict[str, dict[str, str|tuple[str, ...]]. The key is the device ID, the value is a dictionary of the device's
                information.
        """
        raise NotImplementedError("This method must be implemented in the child class")

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
        removed_devices, added_devices = self.changes_from_last_check(update_last_check_devices=update_last_check_devices)
        if on_disconnect is not None:
            for device_id, device_info in removed_devices.items():
                on_disconnect(device_id, device_info)
        if on_connect is not None:
            for device_id, device_info in added_devices.items():
                on_connect(device_id, device_info)

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
        assert self._thread is None, "The USB monitor is already running"
        self._thread = threading.Thread(target=self._monitor_changes,
                                        args=(on_connect, on_disconnect, check_every_seconds),
                                        daemon=True)
        self._thread.start()

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
        assert self._thread is not None, "The USB monitor is not running"
        if self._stop_thread.is_set():
            warn("USB monitor can not be started because it is already stopped. Call stop_monitoring() first",
                 RuntimeWarning)
        while not self._stop_thread.is_set():
            self.check_changes(on_connect=on_connect, on_disconnect=on_disconnect)
            self._stop_thread.wait(check_every_seconds)


    def stop_monitoring(self, warn_if_was_stopped: bool = True) -> None:
        """
        Stops monitoring the USB devices.
        :param warn_if_was_stopped: bool. Whether to warn if the USB monitor was already stopped.
        """
        if self._thread is not None:
            self._stop_thread.set()
            self._thread.join()
            self._thread = None
        elif warn_if_was_stopped:
            warn("USB monitor can not be stopped because it is not running", RuntimeWarning)
        self._stop_thread.clear()

    def __del__(self):
        self.stop_monitoring(warn_if_was_stopped=False)