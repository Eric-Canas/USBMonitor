from __future__ import annotations

from usbmonitor.__platform_specific_detectors._constants import _SECONDS_BETWEEN_CHECKS
from ._usb_detector_base import _USBDetectorBase
from ..attributes import ID_USB_INTERFACES, ID_VENDOR_ID, DEVTYPE, DEVICE_ATTRIBUTES


class _LinuxUSBDetector(_USBDetectorBase):
    def __init__(self):
        import pyudev
        self.context = pyudev.Context()
        self.monitor = None
        self.__TUPLE_ATTRIBUTES_SEPARATORS = {ID_USB_INTERFACES: ':'}
        super(_LinuxUSBDetector, self).__init__()

    def get_current_available_devices(self) -> dict[str, dict[str, str|tuple[str, ...]]]:
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
            device_info = {attr: device.get(attr, "") for attr in DEVICE_ATTRIBUTES}
            device_info = self.__generate_tuple_attributes_from_string(device_info=device_info)
            devices_info[device_id] = device_info

        return devices_info

    def __generate_tuple_attributes_from_string(self, device_info: dict[str, str]) -> dict[str, tuple[str]|str]:
        """
        Generates a tuple of attributes for those attributes that are expected to be a tuple,
        but are stored as a string.
        :param device_info: dict[str, str]. The device information.
        :return: dict[str, tuple[str]|str]. The device information with the tuple attributes.
        """
        for attribute, separator in self.__TUPLE_ATTRIBUTES_SEPARATORS.items():
            if attribute in device_info:
                assert isinstance(device_info[attribute], str), f"The attribute '{attribute}' is expected to be a string"
                # noinspection PyTypeChecker
                device_info[attribute] = tuple(value for value in device_info[attribute].split(separator) if value != "")
        return device_info

    def _monitor_changes(self, on_connect: callable | None = None, on_disconnect: callable | None = None,
                         check_every_seconds: int | float = _SECONDS_BETWEEN_CHECKS) -> None:
        import pyudev

        def __handle_device_event(device):
            action = device.action
            if device.get(DEVTYPE) == 'usb_device':
                device_id = device.device_path
                device_info = {attr: device.get(attr, "") for attr in DEVICE_ATTRIBUTES}
                device_info = self.__generate_tuple_attributes_from_string(device_info=device_info)
                if action == "add" and on_connect is not None:
                    on_connect(device_id, device_info)
                elif action == "remove" and on_disconnect is not None:
                    on_disconnect(device_id, device_info)

        if self.monitor is None:
            self.monitor = pyudev.Monitor.from_netlink(self.context)
            self.monitor.filter_by(subsystem='usb')

        self._thread = pyudev.MonitorObserver(self.monitor, callback=__handle_device_event)

        # Start the observer thread
        self._thread.start()

        # Keep the main thread alive, checking for changes every specified interval
        while not self._stop_thread.is_set():
            self._stop_thread.wait(check_every_seconds)