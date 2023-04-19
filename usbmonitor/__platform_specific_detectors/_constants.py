"""
This file contains constant values and mappings used in the platform-specific USB device detection implementations.
It includes constants for attributes, attribute separators, and regex patterns for specific Operating Systems.
Additionally, it defines the default time interval for checking USB device changes.

Author: Eric-Canas
Date: 28-03-2023
Email: eric@ericcanas.com
Github: https://github.com/Eric-Canas
"""

from ..attributes import ID_MODEL_ID, ID_VENDOR, ID_MODEL, ID_VENDOR_FROM_DATABASE, ID_MODEL_FROM_DATABASE, \
    DEVNAME, ID_USB_CLASS_FROM_DATABASE, ID_USB_INTERFACES, DEVTYPE, ID_VENDOR_ID

_SECONDS_BETWEEN_CHECKS = 0.5

_DEVICE_ID, _PNP_DEVICE_ID = 'DeviceID', 'PNPDeviceID'

_LINUX_TO_WINDOWS_ATTRIBUTES = {
    ID_MODEL_ID: 'HardwareID',
    ID_MODEL: 'Name',
    ID_MODEL_FROM_DATABASE: 'Caption',
    ID_VENDOR_ID: 'HardwareID',
    ID_VENDOR: 'Name',
    ID_VENDOR_FROM_DATABASE: 'Manufacturer',#'Description',
    ID_USB_INTERFACES: 'CompatibleID',
    ID_USB_CLASS_FROM_DATABASE: 'PNPClass',
    DEVNAME: _DEVICE_ID,
    DEVTYPE: _PNP_DEVICE_ID,
}

_LINUX_TUPLE_ATTRIBUTES_SEPARATORS = {ID_USB_INTERFACES: ':'}

_WINDOWS_REGEX_ATTRIBUTES = {ID_MODEL_ID: r'PID_([0-9A-Fa-f]{4})', ID_VENDOR_ID: r'VID_([0-9A-Fa-f]{4})',
                             DEVTYPE: r'^(.+?)\\'}
_WINDOWS_TO_LOWERCASE_ATTRIBUTES = (ID_MODEL_ID, ID_VENDOR_ID)
_WINDOWS_NON_USB_DEVICES_IDS = ("ROOT_HUB20", "ROOT_HUB30")
_WINDOWS_USB_QUERY = f"SELECT {', '.join(set(_LINUX_TO_WINDOWS_ATTRIBUTES.values()))} FROM Win32_PnPEntity " \
                          f"WHERE {_PNP_DEVICE_ID} LIKE 'USB%'"