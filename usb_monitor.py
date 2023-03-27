"""
USBMonitor: A cross-platform USB device connection and disconnection monitor.

Author: Eric-Canas
Date: 24-03-2023
Email: eric@ericcanas.com
Github: https://github.com/Eric-Canas
"""

from __future__ import annotations

import sys
import threading
from time import sleep
from warnings import warn
from abc import ABC, abstractmethod

SECONDS_BETWEEN_CHECKS = 0.5

ID_VENDOR_ID, ID_MODEL_ID, ID_VENDOR, ID_MODEL, ID_SERIAL, ID_USB_INTERFACES, ID_REVISION = \
    'ID_VENDOR_ID', 'ID_MODEL_ID', 'ID_VENDOR', 'ID_MODEL', 'ID_SERIAL', 'ID_USB_INTERFACES', 'ID_REVISION'
DEVNAME, DEVTYPE = 'DEVNAME', 'DEVTYPE'

ID_USB_CLASS_FROM_DATABASE, ID_VENDOR_FROM_DATABASE, ID_MODEL_FROM_DATABASE = \
    'ID_USB_CLASS_FROM_DATABASE', 'ID_VENDOR_FROM_DATABASE', 'ID_MODEL_FROM_DATABASE'

DEVICE_ID, PNP_DEVICE_ID = 'DeviceID', 'PNPDeviceID'

LINUX_TO_WINDOWS_ATTRIBUTES = {
    ID_VENDOR_ID: DEVICE_ID,
    ID_MODEL_ID: 'HardwareID',
    ID_USB_CLASS_FROM_DATABASE: 'PNPClass',
    ID_VENDOR: 'Manufacturer',
    ID_MODEL: 'Name',
    ID_VENDOR_FROM_DATABASE: 'Description',
    ID_MODEL_FROM_DATABASE: 'Caption',
    ID_USB_INTERFACES: 'CompatibleID',
    DEVTYPE: PNP_DEVICE_ID,
}

LINUX_ATTRIBUTES = tuple(LINUX_TO_WINDOWS_ATTRIBUTES.keys())
WINDOWS_TO_LINUX_ATTRIBUTES = {v: k for k, v in LINUX_TO_WINDOWS_ATTRIBUTES.items()}
WINDOWS_USB_QUERY = f"SELECT {', '.join(WINDOWS_TO_LINUX_ATTRIBUTES.keys())} FROM Win32_PnPEntity WHERE {PNP_DEVICE_ID} LIKE 'USB%'"


class USBMonitor:
    def __init__(self):
        if sys.platform.startswith('linux'):
            self.monitor = LinuxUSBDetector()
        elif sys.platform.startswith('win'):
            self.monitor = WindowsUSBDetector()
        elif sys.platform.startswith('darwin'):
            raise NotImplementedError("MacOS is not supported yet")
        else:
            raise NotImplementedError(f"Your OS is not supported: {sys.platform}")

    # When requesting a function that does not exist, it will be redirected to the monitor
    def __getattr__(self, item):
        return getattr(self.monitor, item)

class _USBDetectorBase(ABC):
    def __init__(self):
        self._thread = None
        self._stop_thread = False
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
    def get_current_available_devices(self) -> dict[str, dict[str, str]]:
        """
        Returns a dictionary of the currently available devices, where the key is the device ID and the value is a
        dictionary of the device's information.
        :return: dict[str, dict[str, str]]. The key is the device ID, the value is a dictionary of the device's
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
        assert self._thread is None, "The USB monitor is already running"
        self._thread = threading.Thread(target=self._monitor_changes,
                                        args=(on_connect, on_disconnect, check_every_seconds),
                                        daemon=True)
        self._thread.start()

    def _monitor_changes(self, on_connect: callable | None = None, on_disconnect: callable | None = None,
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
        while not self._stop_thread:
            self.check_changes(on_connect=on_connect, on_disconnect=on_disconnect)
            sleep(check_every_seconds)


    def stop_monitoring(self) -> None:
        """
        Stops monitoring the USB devices.
        """
        if self._thread is not None:
            self._stop_thread = True
            self._thread.join()
            self._thread = None
        else:
            warn("USB monitor can not be stopped because it is not running", RuntimeWarning)
        self._stop_thread = False

    def __del__(self):
        self.stop_monitoring()

class WindowsUSBDetector(_USBDetectorBase):
    def __init__(self):
        self._wmi_interface = None
        super(WindowsUSBDetector, self).__init__()

    def get_current_available_devices(self) -> dict[str, dict[str, str]]:
        """
        Returns a dictionary of the currently available devices, where the key is the device ID and the value is a
        dictionary of the device's information.
        :return: dict[str, dict[str, str]]. The key is the device ID, the value is a dictionary of the device's
                information.
        """
        if self._wmi_interface is None:
            self._wmi_interface = self.__create_wmi_interface()
        devices = self._wmi_interface.query(WINDOWS_USB_QUERY)
        return {getattr(device, DEVICE_ID): {new_name: getattr(device, attribute) for attribute, new_name in WINDOWS_TO_LINUX_ATTRIBUTES.items()}
                for device in devices}

    def _monitor_changes(self, on_connect: callable | None = None, on_disconnect: callable | None = None,
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
        # If running this in a background thread, we MUST create the WMI interface inside the thread.
        self._wmi_interface = self.__create_wmi_interface()
        super(WindowsUSBDetector, self)._monitor_changes(on_connect=on_connect, on_disconnect=on_disconnect,
                                                         check_every_seconds=check_every_seconds)

    def __create_wmi_interface(self):
        from pythoncom import CoInitialize
        CoInitialize()
        import wmi
        # If running this in a background thread, we MUST create the WMI interface inside the thread.
        return wmi.WMI()

class LinuxUSBDetector(_USBDetectorBase):
    def __init__(self):
        import pyudev
        self.context = pyudev.Context()
        self.monitor = None
        super(LinuxUSBDetector, self).__init__()

    def get_current_available_devices(self) -> dict[str, dict[str, str]]:
        """
        Returns a dictionary of the currently available devices, where the key is the device ID and the value is a
        dictionary of the device's information.
        :return: dict[str, dict[str, str]]. The key is the device ID, the value is a dictionary of the device's
                information.
        """
        usb_devices = [device for device in self.context.list_devices(subsystem='usb') if ID_VENDOR_ID in device]
        devices_info = {}
        for device in usb_devices:
            device_id = device.device_path
            device_info = {attr: device.get(attr, "") for attr in LINUX_ATTRIBUTES}
            devices_info[device_id] = device_info

        return devices_info

    def _monitor_changes(self, on_connect: callable | None = None, on_disconnect: callable | None = None,
                        check_every_seconds: int | float = SECONDS_BETWEEN_CHECKS) -> None:
        import pyudev

        if self.monitor is None:
            self.monitor = pyudev.Monitor.from_netlink(self.context)
            self.monitor.filter_by(subsystem='usb')

        def handle_device_event(device):
            action = device.action
            if device.get(DEVTYPE) == 'usb_device':
                device_id = device.device_path
                device_info = {attr: device.get(attr, "") for attr in LINUX_ATTRIBUTES}

                if action == "add" and on_connect is not None:
                    on_connect(device_id, device_info)
                elif action == "remove" and on_disconnect is not None:
                    on_disconnect(device_id, device_info)

        observer = pyudev.MonitorObserver(self.monitor, callback=handle_device_event)

        # Start the observer thread
        observer.start()

        # Keep the main thread alive, checking for changes every specified interval
        while observer.is_alive():
            observer.join(check_every_seconds)


if __name__ == '__main__':
    # Test the USB monitor
    on_connect = lambda device_id, device_info: print(f"Device connected: {device_id} - {device_info}")
    on_disconnect = lambda device_id, device_info: print(f"Device disconnected: {device_id} - {device_info}")
    usb_monitor = USBMonitor()
    usb_monitor.start_monitoring(on_connect=on_connect, on_disconnect=on_disconnect)

    _input = ''
    while _input != 'q':
        _input = input("Monitoring USB connections. Press 'q'+Enter to quit")