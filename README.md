# USBMonitor
<img alt="USBMonitor" title="USBMonitor" src="https://raw.githubusercontent.com/Eric-Canas/USBMonitor/main/resources/logo.png" width="20%" align="left"> USBMonitor is a cross-platform library designed for USB device monitoring. It offers an easy and efficient way to track connections, disconnections, and examine connected device attributes on both Windows and Linux, free from platform-specific nuances or incompatibilities.

## Installation
To install USBMonitor, simply run:

```bash
pip install usbmonitor
```

## Usage
USBMonitor provides a simple and streamlined API to monitor USB device connections and disconnections, as well as to examine device attributes:
`USBMonitor` class

USBMonitor is the unique class you'll be using when working with USBMonitor. It will provide you all the necessary methods to track your USB connections and disconnections, or to check the properties of the current connected devices

## API Reference

### USBMonitor.get_current_available_devices()
Returns a dictionary of the currently available devices, where the key is the `Device ID` and the value is a dictionary containing the device's information. All the keys of this dictionary can be found at `attributes.DEVICE_ATTRIBUTES`. They always correspond with the default Linux device properties (independently of the OS where the library is running).

- Returns: **dict[str, dict[str, str|tuple[str, ...]]]**: A dictionary containing the currently available devices. All values are strings except for `ID_USB_INTERFACES`, which is a tuple `of string`


### USBMonitor.changes_from_last_check(update_last_check_devices = True)
Returns a tuple of two dictionaries, one containing the devices that have been *removed* since the last check, and another one containing the devices that have been *added*. Both dictionaries will have the `Device ID` as key and all the device information as value. Remember that all the keys of this dictionary can be found at can be found at `attributes.DEVICE_ATTRIBUTES`.

- update_last_check_devices: **bool**. If `True` it will update the internal `USBMonitor.last_check_devices` attribute. So the next time you'll call this method, it will check for differences against the devices found in that current call. If `False` it won't update the `USBMonitor.last_check_devices` attribute. 

- Returns: **tuple[dict[str, dict[str, str|tuple[str, ...]]], dict[str, dict[str, str|tuple[str, ...]]]]**: A tuple containing two dictionaries. The first dictionary contains the information of the devices that were removed since the last check and the second dictionary contains the information of the new added devices. All values are `strings` except for `ID_USB_INTERFACES`, which is a `tuple` of `string`.

### USBMonitor.check_changes(on_connect = None, on_disconnect = None, update_last_check_devices = True)
Checks for any new connections or disconnections of USB devices since the last check. If a device has been removed, the `on_disconnect` function will be called with the `Device ID` as the first argument and the dictionary of device information as the second argument. The same will occur with the `on_connect` function if any new device have been added. Internally this function will just run `USBMonitor.changes_from_last_check` and will execute the callbacks for each returned device

- `on_connect`: **callable | None**. The function to call when a device is added. It is expected to have the following format `on_connect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
- on_disconnect: **callable | None**. The function to call when a device is removed. It is expected to have the following format `on_disconnect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
update_last_check_devices: **bool**. If `True` it will update the internal `USBMonitor.last_check_devices` attribute. So the next time you'll call this method, it will check for differences against the devices found in that current call. If `False` it won't update the `USBMonitor.last_check_devices` attribute. 

### Device Properties
