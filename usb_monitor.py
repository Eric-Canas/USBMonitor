"""
The USBMonitor class allows to monitor for the connection and disconnection of USB devices, in a cross-platform way.
It frees the developer from having to deal with the differences between the different operating systems.
In its guts, it is based on the `wmi` package for Windows and the `pyudev` package for Linux.

Author: Eric-Canas
Date: 24-03-2023
Email: eric@ericcanas.com
Github: https://github.com/Eric-Canas
"""

from __future__ import annotations

import sys
import threading
from time import sleep
from loguru import logger

SECONDS_BETWEEN_CHECKS = 0.5

class USBMonitor:
    def __init__(self):
        """
        """
        if sys.platform.startswith('linux'):
            self.monitor = LinuxUSBDetector()
        elif sys.platform.startswith('win'):
            self.monitor = WindowsUSBDetector()

    # When requesting a function that does not exist, it will be redirected to the monitor
    def __getattr__(self, item):
        return getattr(self.monitor, item)

class WindowsUSBDetector:
    def __init__(self):
        import wmi
        self._wmi_interface = wmi.WMI()
        self.lock = threading.Lock()
        self.on_start_devices = self.get_current_available_devices()
        self.last_check_devices = self.on_start_devices.copy()

        self.__thread = None
        self.__stop_thread = False

    def changes_from_last_check(self, update_last_check_devices:bool = True) -> tuple[dict[str, str], dict[str, str]]:
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

    def get_current_available_devices(self) -> dict[str, dict[str, str]]:
        """
        Returns a dictionary of the currently available devices, where the key is the device ID and the value is a
        dictionary of the device's information.
        :return: dict[str, dict[str, str]]. The key is the device ID, the value is a dictionary of the device's
                information.
        """
        CAPTION, CLASS_GUID, DEVICE_ID, NAME, PNP_CLASS, STATUS, SERVICE = "Caption", "ClassGuid", "DeviceID", "Name", \
                                                                           "PNPClass", "Status", "Service"
        ATTRIBUTES = (NAME, DEVICE_ID, CAPTION, CLASS_GUID, PNP_CLASS, SERVICE, STATUS)
        devices = self._wmi_interface.query(f"SELECT * FROM Win32_PnPEntity WHERE Caption LIKE '%USB%'")
        return {getattr(device, DEVICE_ID): {attribute: getattr(device, attribute) for attribute in ATTRIBUTES}
                for device in devices}

    def check_changes(self, on_connect: callable|None = None, on_disconnect: callable|None = None,
                      update_last_check_devices:bool = True) -> None:
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
                         check_every_seconds: int | float = SECONDS_BETWEEN_CHECKS) -> None:
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
        assert self.__thread is None, "The USB monitor is already running"
        self.__thread = threading.Thread(target=self.__monitor_changes,
                                         args=(on_connect, on_disconnect, check_every_seconds),
                                         daemon=True)
        self.__thread.start()
        #self.__monitor_changes(on_connect, on_disconnect, check_every_seconds)

    def __monitor_changes(self, on_connect: callable | None = None, on_disconnect: callable | None = None,
                         check_every_seconds: int | float = SECONDS_BETWEEN_CHECKS) -> None:
        """
        Monitors the USB devices. This function should ALWAYS be called from a background thread.
        :param on_connect: callable | None. The function to call when a device is added. It is expected to receive two
                arguments, the device ID and the device information. on_connect(device_id: str, device_info: dict[str, str])
        :param on_disconnect: callable | None. The function to call when a device is removed. It is expected to receive
                two arguments, the device ID and the device information. on_disconnect(device_id: str, device_info: dict[str, str])
        :param check_every_seconds: int | float. The number of seconds to wait between each check for changes in the
                USB devices. Defaults to 0.5 seconds.
        """
        # Create the WMI interface in the thread
        from pythoncom import CoInitialize
        CoInitialize()
        import wmi
        self._wmi_interface = wmi.WMI()
        while not self.__stop_thread:
            self.check_changes(on_connect=on_connect, on_disconnect=on_disconnect)
            sleep(check_every_seconds)

    def stop_monitoring(self) -> None:
        """
        Stops monitoring the USB devices.
        """
        if self.__thread is not None:
            self.__stop_thread = True
            self.__thread.join()
            self.__thread = None
        else:
            logger.warning("USB monitor can not be stopped because it is not running")
        self.__stop_thread = False

class LinuxUSBDetector:
    def __init__(self):
        import pyudev
        self.devices = {}
        self.keyboard_vendor_id = 0x045e  # Example vendor ID for a keyboard

        context = pyudev.Context()
        for device in context.list_devices(subsystem='usb'):
            self.devices[device.device_node] = device
            if device.get('ID_VENDOR_ID') == hex(self.keyboard_vendor_id)[2:]:
                print('Found keyboard:', device.device_node)

    def start_monitoring(self, on_detach):
        import pyudev
        monitor = pyudev.Monitor.from_netlink(pyudev.Context())
        monitor.filter_by(subsystem='usb')
        for device in iter(monitor.poll, None):
            if device.action == 'remove' and device.device_node in self.devices:
                del self.devices[device.device_node]
                on_detach(device)



if __name__ == '__main__':
    # Test the USB monitor
    on_connect = lambda device_id, device_info: print(f"Device connected: {device_id} - {device_info}")
    on_disconnect = lambda device_id, device_info: print(f"Device disconnected: {device_id} - {device_info}")
    usb_monitor = USBMonitor()
    usb_monitor.start_monitoring(on_connect=on_connect, on_disconnect=on_disconnect)

    _input = ''
    while _input != 'q':
        _input = input("Monitoring USB connections. Press 'q'+Enter to quit")