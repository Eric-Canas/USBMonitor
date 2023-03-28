"""
USBMonitor: USBMonitor is an easy-to-use cross-platform library for USB device monitoring that simplifies
            tracking of connections, disconnections, and examination of connected device attributes on both
            Windows and Linux, freeing the user from platform-specific details or incompatibilities.

Author: Eric-Canas
Date: 24-03-2023
Email: eric@ericcanas.com
Github: https://github.com/Eric-Canas
"""

from __future__ import annotations

import sys


class USBMonitor:
    def __init__(self):
        if sys.platform.startswith('linux'):
            from .__platform_specific_detectors._linux_usb_detector import _LinuxUSBDetector
            self.monitor = _LinuxUSBDetector()
        elif sys.platform.startswith('win'):
            from .__platform_specific_detectors._windows_usb_detector import _WindowsUSBDetector
            self.monitor = _WindowsUSBDetector()
        elif sys.platform.startswith('darwin'):
            raise NotImplementedError("MacOS is not supported yet")
        else:
            raise NotImplementedError(f"Your OS is not supported: {sys.platform}")

    # When requesting a function that does not exist, it will be redirected to the monitor
    def __getattr__(self, item):
        return getattr(self.monitor, item)