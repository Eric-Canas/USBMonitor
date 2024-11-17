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
    DEVNAME, ID_USB_CLASS_FROM_DATABASE, ID_USB_INTERFACES, DEVTYPE, ID_VENDOR_ID, ID_SERIAL

_SECONDS_BETWEEN_CHECKS = 0.5
_THREAD_JOIN_TIMEOUT_SECONDS = 5

_DEVICE_ID, _PNP_DEVICE_ID = 'DeviceID', 'PNPDeviceID'

_LINUX_TO_WINDOWS_ATTRIBUTES = {
    ID_MODEL_ID: 'HardwareID',
    ID_MODEL: 'Name',
    ID_MODEL_FROM_DATABASE: 'Caption',
    ID_VENDOR_ID: 'HardwareID',
    ID_VENDOR: 'Name',
    ID_VENDOR_FROM_DATABASE: 'Manufacturer',
    ID_USB_INTERFACES: 'CompatibleID',
    ID_USB_CLASS_FROM_DATABASE: 'PNPClass',
    DEVNAME: _DEVICE_ID,
    DEVTYPE: _PNP_DEVICE_ID,
    ID_SERIAL: _PNP_DEVICE_ID
}

_LINUX_TUPLE_ATTRIBUTES_SEPARATORS = {ID_USB_INTERFACES: ':'}

USB, USBSTOR, USB4, USBPRINT = 'USB', 'USBSTOR', 'USB4', 'USBPRINT'

_WINDOWS_USB_REGEX_ATTRIBUTES = {ID_MODEL_ID: r'PID_([0-9A-Fa-f]{4})', ID_VENDOR_ID: r'VID_([0-9A-Fa-f]{4})',
                                 DEVTYPE: r'^(.+?)\\', ID_SERIAL: r'\\([^\\]+)$'}
_WINDOWS_USB4_REGEX_ATTRIBUTES = {ID_MODEL_ID: r'PID_([0-9A-Fa-f]{4})', ID_VENDOR_ID: r'VID_([0-9A-Fa-f]{4})',
                                  DEVTYPE: r'^(.+?)\\', ID_SERIAL: r'\\([^\\]+)$'}
_WINDOWS_USBPRINT_REGEX_ATTRIBUTES = {ID_MODEL_ID: r'PID_([0-9A-Fa-f]{4})', ID_VENDOR_ID: r'VID_([0-9A-Fa-f]{4})',
                                        DEVTYPE: r'^(.+?)\\', ID_SERIAL: r'\\([^\\]+)$'}
_WINDOWS_USBSTOR_REGEX_ATTRIBUTES = {ID_MODEL_ID: r'PROD_([a-zA-Z0-9\_\/\.\-]{2,16})&', ID_VENDOR_ID: r'VEN_([a-zA-Z0-9\.\_\-\/]{2,8})&',
                                     DEVTYPE: r'^(.+?)\\', ID_SERIAL: r'\\([^\\]+)$'}

_WINDOWS_REGEX_ATTRIBUTES_BY_DRIVER = {USB: _WINDOWS_USB_REGEX_ATTRIBUTES,
                                       USBSTOR: _WINDOWS_USBSTOR_REGEX_ATTRIBUTES,
                                       USB4: _WINDOWS_USB4_REGEX_ATTRIBUTES,
                                       USBPRINT: _WINDOWS_USBPRINT_REGEX_ATTRIBUTES}

_WINDOWS_TO_LOWERCASE_ATTRIBUTES = (ID_MODEL_ID, ID_VENDOR_ID)
_WINDOWS_NON_USB_DEVICES_IDS = ("ROOT_HUB20", "ROOT_HUB30", "VIRTUAL_POWER_PDO")
_WINDOWS_USB_QUERY = f"SELECT {', '.join(set(_LINUX_TO_WINDOWS_ATTRIBUTES.values()))} FROM Win32_PnPEntity " \
                          f"WHERE {_PNP_DEVICE_ID} LIKE 'USB%'"

# Darwin-specific constants
_DARWIN_TO_LINUX_ATTRIBUTES = {
    ID_MODEL_ID: 'idProduct',
    ID_MODEL: 'kUSBProductString',
    ID_MODEL_FROM_DATABASE: 'USB Product Name',
    ID_VENDOR_ID: 'idVendor',
    ID_VENDOR: 'kUSBVendorString',
    ID_VENDOR_FROM_DATABASE: 'USB Vendor Name',
    ID_USB_INTERFACES: 'IOCFPlugInTypes',
    ID_USB_CLASS_FROM_DATABASE: 'bDeviceClass',
    DEVNAME: 'BSD Name',
    DEVTYPE: 'Device Speed',
    ID_SERIAL: 'kUSBSerialNumberString',
}

_DARWIN_REGEX_ATTRIBUTES = {
    ID_MODEL_ID: r'idProduct: ([0-9A-Fa-f]{4})',
    ID_VENDOR_ID: r'idVendor: ([0-9A-Fa-f]{4})'
}
