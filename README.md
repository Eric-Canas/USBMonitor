# USBMonitor
<img alt="USBMonitor" title="USBMonitor" src="https://raw.githubusercontent.com/Eric-Canas/USBMonitor/main/resources/logo.png" width="20%" align="left"> **USBMonitor** is a versatile **cross-platform** library that simplifies **USB device monitoring** for both _Windows_ and _Linux_ systems. It enables developers to effortlessly track device **connections**, **disconnections**, and access to all connected device **attributes**.

With **USBMonitor**, developers can stay up-to-date with any changes in the connected USB devices, allowing them to **trigger specific actions** whenever a USB device is connected or disconnected. By ensuring **consistent functionality across various operating systems**, **USBMonitor** removes the need to address platform-specific quirks, inconsistencies, or incompatibilities, resulting in a smooth and efficient USB device management experience. The uniformity in functionality significantly enhances **code compatibility**, minimizing the risk of **code issues** or **unexpected breaks** when moving between platforms.

At its core, **USBMonitor** utilizes <a href="https://pyudev.readthedocs.io/en/latest/" target="_blank">pyudev</a> (for Linux environments) and <a href="https://github.com/mhammond/pywin32" target="_blank">WMI</a> (for Windows environments), handling all the low-level intricacies and translating OS-specific information to ensure consistency across both systems.

## Installation
To install **USBMonitor**, simply run:

```bash
pip install usb-monitor
```

## Usage
Using **USBMonitor** is both simple and straight-forward. In most cases, you'll just want to start the [monitoring _Daemon_](#usbmonitorstart_monitoringon_connect--none-on_disconnect--none-check_every_seconds--05), defining the `on_connect` and `on_disconnect` callback functions to manage events when a USB device connects or disconnects. Here's a basic example:

```python
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID

device_info_str = lambda device_info: f"{device_info[ID_MODEL]} ({device_info[ID_MODEL_ID]} - {device_info[ID_VENDOR_ID]})"
# Define the `on_connect` and `on_disconnect` callbacks
on_connect = lambda device_id, device_info: print(f"Connected: {device_info_str(device_info=device_info)}")
on_disconnect = lambda device_id, device_info: print(f"Disconnected: {device_info_str(device_info=device_info)}")

# Create the USBMonitor instance
monitor = USBMonitor()

# Start the daemon
monitor.start_monitoring(on_connect=on_connect, on_disconnect=on_disconnect)

# ... Rest of your code ...

# If you don't need it anymore stop the daemon
monitor.stop_monitoring()
```
Output
<div align="center">

Linux | Windows
:---: | :---:
![](https://raw.githubusercontent.com/Eric-Canas/USBMonitor/main/resources/linux_monitor.gif) | ![](https://raw.githubusercontent.com/Eric-Canas/USBMonitor/main/resources/windows_monitor.gif)

</div>


Sometimes, when initializing your software, you may seek to confirm which USB devices are indeed connected. 

```python
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID

# Create the USBMonitor instance
monitor = USBMonitor()

# Get the current devices
devices_dict = monitor.get_available_devices()

# Print them
for device_id, device_info in devices_dict.items():
    print(f"{device_id} -- {device_info[ID_MODEL]} ({device_info[ID_MODEL_ID]} - {device_info[ID_VENDOR_ID]})")
```
Output
```bash
/dev/bus/usb/001/001 -- xHCI_Host_Controller (0002 - 1d6b)
/dev/bus/usb/001/002 -- USB2.0_Hub (3431 - 2109)
/dev/bus/usb/001/003 -- USB_Optical_Mouse (c077 - 046d)
/dev/bus/usb/001/004 -- USB_Compliant_Keypad (9881 - 05a4)
/dev/bus/usb/002/001 -- xHCI_Host_Controller (0003 - 1d6b)
```



## API Reference

### USBMonitor.start_monitoring(on_connect = None, on_disconnect = None, check_every_seconds = 0.5)
Starts a daemon that continuously monitors the connected USB devices in order to detect new connections or disconnections. When a device is disconnected, the `on_disconnect` callback function is invoked with the Device ID ([`devname`](#device-properties)) as the first argument and the [dictionary of device information](#device-properties) as the second argument. Similarly, when a new device is connected, the `on_connect` callback function is called with the same arguments. This allows developers to promptly respond to any changes in the connected USB devices and perform necessary actions.

- `on_connect`: **callable | None**. The function to call every time a device is **added**. It is expected to have the following format `on_connect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
- `on_disconnect`: **callable | None**. The function to call every time a device is **removed**. It is expected to have the following format `on_disconnect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
- `check_every_seconds`: **int | float**. Seconds to wait between each check for changes in the USB devices. Default value is 0.5 seconds.

### USBMonitor.stop_monitoring(warn_if_was_stopped=True)
Stops the monitoring of USB devices. This function will **stop** the daemon launched by `USBMonitor.start_monitoring`

- `warn_if_was_stopped`: **bool**. If set to `True`, this function will issue a warning if the monitoring of USB devices was already stopped (the daemon was not running).


### USBMonitor.get_available_devices()
Returns a dictionary of the currently available devices, where the key is the `Device ID` ([`devname`](#device-properties)) and the value is a [dictionary containing the device's information](#device-properties). All the keys of this dictionary can be found at `attributes.DEVICE_ATTRIBUTES`. They always correspond with the default Linux device properties (independently of the OS where the library is running).

- Returns: **dict[str, dict[str, str|tuple[str, ...]]]**: A dictionary containing the currently available devices. All values are strings except for `ID_USB_INTERFACES`, which is a `tuple` of `string`



### USBMonitor.changes_from_last_check(update_last_check_devices = True)
Returns a tuple of two dictionaries, one containing the devices that have been *removed* since the last check, and another one containing the devices that have been *added*. Both dictionaries will have the `Device ID` ([`devname`](#device-properties)) as key and all the device information as value. Remember that all the [keys of this dictionary](#device-properties) can be found at can be found at `attributes.DEVICE_ATTRIBUTES`.

- `update_last_check_devices`: **bool**. If `True` it will update the internal `USBMonitor.last_check_devices` attribute. So the next time you'll call this method, it will check for differences against the devices found in that current call. If `False` it won't update the `USBMonitor.last_check_devices` attribute. 

- Returns: **tuple[dict[str, dict[str, str|tuple[str, ...]]], dict[str, dict[str, str|tuple[str, ...]]]]**: A `tuple` containing two `dictionaries`. The first `dictionary` contains the information of the devices that were **removed** since the last check and the second dictionary contains the information of the new **added** devices. All values are `strings` except for `ID_USB_INTERFACES`, which is a `tuple` of `string`.

### USBMonitor.check_changes(on_connect = None, on_disconnect = None, update_last_check_devices = True)
Checks for any new connections or disconnections of USB devices since the last check. If a device has been removed, the `on_disconnect` function will be called with the `Device ID` as the first argument and the [dictionary with the device's information](#device-properties) as the second argument. The same will occur with the `on_connect` function if any new device have been added. Internally this function will just run `USBMonitor.changes_from_last_check` and will execute the callbacks for each returned device

- `on_connect`: **callable | None**. The function to call when a device is added. It is expected to have the following format `on_connect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
- `on_disconnect`: **callable | None**. The function to call when a device is removed. It is expected to have the following format `on_disconnect(device_id: str, device_info: dict[str, dict[str, str|tuple[str, ...]]])`
- `update_last_check_devices`: **bool**. If `True` it will update the internal `USBMonitor.last_check_devices` attribute. So the next time you'll call this method, it will check for differences against the devices found in that current call. If `False` it won't update the `USBMonitor.last_check_devices` attribute. 

### Device Properties

The `device_info` returned by most functions will contain the following information:

<table>
  <thead>
    <tr>
      <th style="min-width:150px">Key</th>
      <th style="min-width:400px">Value Description</th>
      <th style="min-width:150px">Example (Linux)</th>
      <th style="min-width:150px">Example (Windows)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>'ID_MODEL_ID'</code></td>
      <td>The product ID of the USB device.</td>
      <td><code>'0892'</code></td>
      <td><code>'0892'</code></td>
    </tr>
    <tr>
      <td><code>'ID_MODEL'</code></td>
      <td>The name of the USB device model.</td>
      <td><code>'HD_Pro_Webcam_C920'</code></td>
      <td><code>'HD Pro Webcam C920'</code></td>
    </tr>
    <tr>
      <td><code>'ID_MODEL_FROM_DATABASE'</code></td>
      <td>Device model name, retrieved from the device database.</td>
      <td><code>'OrbiCam'</code></td>
      <td><code>'HD Pro Webcam C920'</code></td>
    </tr>
    <tr>
      <td><code>'ID_VENDOR'</code></td>
      <td>The name of the USB device vendor.</td>
      <td><code>'046d'</code></td>
      <td><code>'HD Pro Webcam C920'</code></td>
    </tr>
    <tr>
      <td><code>'ID_VENDOR_ID'</code></td>
      <td>The vendor ID of the USB device.</td>
      <td><code>'046d'</code></td>
      <td><code>'046d'</code></td>
    </tr>
    <tr>
      <td><code>'ID_VENDOR_FROM_DATABASE'</code></td>
      <td>USB device vendor's name, from the device database.</td>
      <td><code>'Logitech, Inc.'</code></td>
      <td><code>'Logitech'</code></td>
    </tr>
    <tr>
      <td><code>'ID_USB_INTERFACES'</code></td>
      <td>A <code>tuple</code> representing the USB device's interfaces.</td>
      <td><code>('0e0100', ...)</code></td>
      <td><code>('USB\Class_0e', ...)</code></td>
    </tr>
    <tr>
      <td><code>'DEVNAME'</code></td>
      <td>The device name or path.</td>
      <td><code>'/dev/bus/usb/001/003'</code></td>
      <td><code>'...6&26FD4D64&1&0000'</code></td>
    </tr>
    <tr>
      <td><code>'DEVTYPE'</code></td>
      <td>Should always be <code>'usb_device'</code>.</td>
      <td><code>'usb_device'</code></td>
      <td><code>'USB'</code></td>
    </tr>
  </tbody>
</table>

Note that, depending on the device and the OS, some of this information may be incomplete or certain attributes may overlap with others.

## Roadmap

- Accepting MacOS (As soon as I will have access to a MacOS system to test it out)
- Include an attribute with an identifier to differentiate identical devices

