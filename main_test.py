from usbmonitor import USBMonitor

if __name__ == '__main__':
    # Test the USB monitor
    on_connect = lambda device_id, device_info: print(f"Device connected: {device_id} - {device_info}")
    on_disconnect = lambda device_id, device_info: print(f"Device disconnected: {device_id} - {device_info}")
    usb_monitor = USBMonitor()
    usb_monitor.start_monitoring(on_connect=on_connect, on_disconnect=on_disconnect)

    _input = ''
    while _input != 'q':
        _input = input("Monitoring USB connections. Press 'q'+Enter to quit")
    usb_monitor.stop_monitoring()