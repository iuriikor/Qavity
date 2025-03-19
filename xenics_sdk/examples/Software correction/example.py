"""
Software correction example
"""

import sys
import os
from xenics.xeneth.capi.enums import XFilterMessage
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera

def main(url):
    """
    Main program function
    """
    cam = XCamera()

    try:
        # Open connection to the camera
        print(f"Open connection to '{url}'")
        cam.open(url)

        packname = os.path.join(os.path.dirname(__file__), "pack.xca")

        # When the connection is initialised, ...
        if cam.is_initialized:
            try:
                print("Loading the calibration pack.")
                cam.load_calibration(packname, 0)

                fltSoftwareCorrection = cam.filter_queue("SoftwareCorrection", "")

                if fltSoftwareCorrection > 0:
                    print("Software Correction initialised.")

                    # Receive the XML stream to output to console.
                    stream = cam.filter_recv_stream(fltSoftwareCorrection, XFilterMessage.XMsgSerialise)

                    print(f"Parameters:\n{stream}")

                else:
                    print("Failed initialising the software correction.")
            except XenethAPIException as e:
                print(f"Error when loading the calibration pack: {e}")
        else:
            print("Initialization failed")

    except XenethAPIException as e:
        print(f"An error occurred: {e}")

    finally:
        # Cleanup
        if cam.is_initialized:
            print("Closing connection to camera.")
            cam.close()

if __name__ == "__main__":
        
    url = "cam://0"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
