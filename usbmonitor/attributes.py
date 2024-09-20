"""
device_info dictionary attributes. Same attributes as Linux udev (independently of the OS where the library is running).
All these attributes are the keys of the device_info dictionary returned by the `get_available_devices` method.
The expected values of these attributes are all strings, except for the `ID_USB_INTERFACES` attribute, which is a tuple.

Author: Eric-Canas
Date: 26-03-2023
Email: eric@ericcanas.com
Github: https://github.com/Eric-Canas
"""

ID_VENDOR_ID = 'ID_VENDOR_ID'
ID_VENDOR = 'ID_VENDOR'
ID_MODEL = 'ID_MODEL'
ID_MODEL_ID = 'ID_MODEL_ID'
ID_SERIAL = 'ID_SERIAL'
ID_USB_INTERFACES = 'ID_USB_INTERFACES'
ID_REVISION = 'ID_REVISION'

ID_USB_CLASS_FROM_DATABASE = 'ID_USB_CLASS_FROM_DATABASE'
ID_VENDOR_FROM_DATABASE = 'ID_VENDOR_FROM_DATABASE'
ID_MODEL_FROM_DATABASE = 'ID_MODEL_FROM_DATABASE'

DEVNAME = 'DEVNAME'
DEVTYPE = 'DEVTYPE'

DEVICE_ATTRIBUTES = (ID_MODEL_ID, ID_MODEL, ID_MODEL_FROM_DATABASE, ID_VENDOR, ID_VENDOR_ID, ID_VENDOR_FROM_DATABASE,
                     ID_USB_INTERFACES, ID_USB_CLASS_FROM_DATABASE, DEVNAME, DEVTYPE, ID_SERIAL)
