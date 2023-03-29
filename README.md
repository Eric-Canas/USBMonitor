# USBMonitor
<img alt="USBMonitor" title="USBMonitor" src="https://raw.githubusercontent.com/Eric-Canas/USBMonitor/main/resources/logo.png" width="20%" align="left"> **USBMonitor** is a versatile **cross-platform** library that simplifies **USB device monitoring** for both _Windows_ and _Linux_ systems. It enables developers to effortlessly track device **connections**, **disconnections**, and access to all connected device **attributes**.

With **USBMonitor**, developers can stay up-to-date with any changes in the connected USB devices, allowing them to **trigger specific actions** whenever a USB device is connected or disconnected. By ensuring **consistent functionality across various operating systems**, **USBMonitor** removes the need to address platform-specific quirks, inconsistencies, or incompatibilities, resulting in a smooth and efficient USB device management experience. The uniformity in functionality significantly enhances **code compatibility**, minimizing the risk of **code issues** or **unexpected breaks** when moving between platforms.

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

### USBMonitor.start_monitoring(on_connect = None, on_disconnect = None, check_every_seconds = 0.5)
Starts a daemon that continuously monitors the connected USB devices in order to detect new connections or disconnections. When a device is disconnected, the `on_disconnect` callback function is invoked with the Device ID as the first argument and the dictionary of device information as the second argument. Similarly, when a new device is connected, the `on_connect` callback function is called with the same arguments. This allows developers to promptly respond to any changes in the connected USB devices and perform necessary actions.

- `on_connect`: **callable | None**. The function to call every time a device is **added**. It is expected to have the following format `on_connect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
- `on_disconnect`: **callable | None**. The function to call every time a device is **removed**. It is expected to have the following format `on_disconnect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
- `check_every_seconds`: **int | float**. Seconds to wait between each check for changes in the USB devices. Default value is 0.5 seconds.

### USBMonitor.stop_monitoring(warn_if_was_stopped=True)
Stops the monitoring of USB devices. This function will **stop** the daemon launched by `USBMonitor.start_monitoring`

- `warn_if_was_stopped`: **bool**. If set to `True`, this function will issue a warning if the monitoring of USB devices was already stopped (the daemon was not running).


### USBMonitor.get_current_available_devices()
Returns a dictionary of the currently available devices, where the key is the `Device ID` and the value is a dictionary containing the device's information. All the keys of this dictionary can be found at `attributes.DEVICE_ATTRIBUTES`. They always correspond with the default Linux device properties (independently of the OS where the library is running).

- Returns: **dict[str, dict[str, str|tuple[str, ...]]]**: A dictionary containing the currently available devices. All values are strings except for `ID_USB_INTERFACES`, which is a `tuple` of `string`



### USBMonitor.changes_from_last_check(update_last_check_devices = True)
Returns a tuple of two dictionaries, one containing the devices that have been *removed* since the last check, and another one containing the devices that have been *added*. Both dictionaries will have the `Device ID` as key and all the device information as value. Remember that all the keys of this dictionary can be found at can be found at `attributes.DEVICE_ATTRIBUTES`.

- `update_last_check_devices`: **bool**. If `True` it will update the internal `USBMonitor.last_check_devices` attribute. So the next time you'll call this method, it will check for differences against the devices found in that current call. If `False` it won't update the `USBMonitor.last_check_devices` attribute. 

- Returns: **tuple[dict[str, dict[str, str|tuple[str, ...]]], dict[str, dict[str, str|tuple[str, ...]]]]**: A tuple containing two dictionaries. The first dictionary contains the information of the devices that were removed since the last check and the second dictionary contains the information of the new added devices. All values are `strings` except for `ID_USB_INTERFACES`, which is a `tuple` of `string`.

### USBMonitor.check_changes(on_connect = None, on_disconnect = None, update_last_check_devices = True)
Checks for any new connections or disconnections of USB devices since the last check. If a device has been removed, the `on_disconnect` function will be called with the `Device ID` as the first argument and the dictionary of device information as the second argument. The same will occur with the `on_connect` function if any new device have been added. Internally this function will just run `USBMonitor.changes_from_last_check` and will execute the callbacks for each returned device

- `on_connect`: **callable | None**. The function to call when a device is added. It is expected to have the following format `on_connect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
- `on_disconnect`: **callable | None**. The function to call when a device is removed. It is expected to have the following format `on_disconnect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
`update_last_check_devices`: **bool**. If `True` it will update the internal `USBMonitor.last_check_devices` attribute. So the next time you'll call this method, it will check for differences against the devices found in that current call. If `False` it won't update the `USBMonitor.last_check_devices` attribute. 

### Device Properties
