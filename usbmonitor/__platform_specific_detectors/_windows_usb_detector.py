from __future__ import annotations
import re
from warnings import warn


from ._usb_detector_base import _USBDetectorBase
from ..attributes import ID_MODEL_ID, ID_VENDOR, DEVTYPE
from usbmonitor.__platform_specific_detectors._constants import _DEVICE_ID, _PNP_DEVICE_ID, _LINUX_TO_WINDOWS_ATTRIBUTES, _SECONDS_BETWEEN_CHECKS


class _WindowsUSBDetector(_USBDetectorBase):
    __REGEX_ATTRIBUTES = {ID_MODEL_ID: r'PID_([0-9A-Fa-f]{4})', ID_VENDOR: r'VID_([0-9A-Fa-f]{4})',
                          DEVTYPE: r'^(.+?)\\'}
    __WINDOWS_USB_QUERY = f"SELECT {', '.join(set(_LINUX_TO_WINDOWS_ATTRIBUTES.values()))} FROM Win32_PnPEntity " \
                          f"WHERE {_PNP_DEVICE_ID} LIKE 'USB%'"
    __NON_USB_DEVICES_IDS = ("ROOT_HUB20", "ROOT_HUB30")
    def __init__(self):
        self._wmi_interface = None
        # CONSTANTS
        super(_WindowsUSBDetector, self).__init__()

    def get_current_available_devices(self) -> dict[str, dict[str, str]]:
        """
        Returns a dictionary of the currently available devices, where the key is the device ID and the value is a
        dictionary of the device's information.
        :return: dict[str, dict[str, str]]. The key is the device ID, the value is a dictionary of the device's
                information.
        """
        if self._wmi_interface is None:
            self._wmi_interface = self.__create_wmi_interface()
        devices = self._wmi_interface.query(_WindowsUSBDetector.__WINDOWS_USB_QUERY)
        devices = {getattr(device, _DEVICE_ID): {new_name: getattr(device, attribute)
                                                 for new_name, attribute in _LINUX_TO_WINDOWS_ATTRIBUTES.items()}
                    for device in devices}
        devices = self.__filter_devices(devices=devices)
        devices = self.__finetune_regex_attributes(devices=devices)
        return devices

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
        # If running this in a background thread, we MUST create the WMI interface inside the thread.
        self._wmi_interface = self.__create_wmi_interface()
        super(_WindowsUSBDetector, self)._monitor_changes(on_connect=on_connect, on_disconnect=on_disconnect,
                                                         check_every_seconds=check_every_seconds)

    def __filter_devices(self, devices: dict[str, dict[str, tuple[str]|str]]) -> dict[str, dict[str, tuple[str]|str]]:
        """
        Filters the devices to only include the ones that are USB devices.
        :param devices: dict[str, dict[str, str]]. The dictionary of devices to filter.
        :return: dict[str, dict[str, str]]. The filtered devices.
        """
        return {device_id: device_info for device_id, device_info in devices.items()
                if not any(substring in device_info[DEVTYPE] for substring in _WindowsUSBDetector.__NON_USB_DEVICES_IDS)}

    def __finetune_regex_attributes(self, devices: dict[str, dict[str | tuple[str, ...]]]) -> dict[str, dict[str, str]]:
        """
        Transforms some attributes to be more similar to the Linux attributes.
        :param devices: dict[str, str|tuple[str,...]]. The dictionary of devices to transform.
        :return: dict[str, dict[str, str]]. The transformed devices.
        """
        for device_id, device_info in devices.items():
            new_attributes = {attribute: self.__apply_regex(device_info[attribute], regex)
                              for attribute, regex in _WindowsUSBDetector.__REGEX_ATTRIBUTES.items()
                              if attribute in device_info}
            device_info.update(new_attributes)
        return devices

    def __apply_regex(self, value: tuple[str] | str, regex: str) -> str:
        """
        Apply the regex to a value, taking into account if it is a tuple or not.
        :param value: tuple[str] | str. The value to apply the regex to.
        :param regex: str. The regex to apply.
        :return: str. The value after applying the regex.
        """
        if isinstance(value, str):
            value = (value,)
        values_found = []
        for value in value:
            match = re.search(regex, value)
            if match is not None:
                values_found.append(match.group(1))
        # If no value was found, return the original value
        if len(values_found) == 0:
            warn(f"Could not find a value for the regex '{regex}' in the value '{value}'")
            return value
        # Otherwise, return check there are no inconsistencies and return the value
        assert all(value == values_found[0] for value in values_found), "The values found are not all the same"
        return values_found[0]


    def __create_wmi_interface(self):
        from pythoncom import CoInitialize
        CoInitialize()
        import wmi
        # If running this in a background thread, we MUST create the WMI interface inside the thread.
        return wmi.WMI()