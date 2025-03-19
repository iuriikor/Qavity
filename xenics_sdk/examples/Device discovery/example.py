"""
Device discovery example.
"""

import sys
import os
os.add_dll_directory("C:\\Users\\CavLev\\Documents\\Qavity\\dll")

# import all from high level API
from xenics.xeneth import XEnumerationFlags, XDeviceStates, enumerate_devices
from xenics.xeneth.errors import XenethException


def main():
    """
    Main program
    """

    # enumerate all
    flags = XEnumerationFlags.XEF_EnableAll

    try:
        # enumerate devices
        devices = enumerate_devices(flags)

        if len(devices) == 0:
            print("No devices found")
            sys.exit()

        states = {XDeviceStates.XDS_Available : "Available",
                XDeviceStates.XDS_Busy : "Busy",
                XDeviceStates.XDS_Unreachable : "Unreachable"}

        for idx, dev in enumerate(devices):
            print(f"Device[{idx}] {dev.name} @ {dev.address} ({dev.transport})")
            print(f"PID: {dev.pid}")
            print(f"Serial: {dev.serial}")
            print(f"URL: {dev.url}")
            print(f"State: {states[dev.state]} ({dev.state})\n")

    except XenethException as e:
        print(f"Error occurred during device discovery: {e.message}")


if __name__ == '__main__':
    main()
