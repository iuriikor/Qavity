"""
XPNG thermography example
"""

import os
import sys
from xenics.xeneth.capi.enums import XFrameType, XGetFrameFlags, XSaveDataFlags
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera

def main(url):

    # Calibration pack path - specific to the camera
    # This example is created using the Gobi+ 640 GigE (pid: 0xF229) camera.
    # Please make sure to use a calibration file for the camera you are using
    packname = os.path.join(os.path.dirname(__file__), "pack.xca")

    # Create an instance of the XCamera class
    cam = XCamera()

    try:
        print("Opening connection to {url}")
        cam.open(url) # Open connection to the camera

        if cam.is_initialized: # If the connection is initialized
            try:
                print("Start capturing.")
                cam.start_capture() # Start capturing

                if cam.is_capturing: # If the camera is capturing

                    cam.load_calibration(packname, 0) # Load calibration pack

                    # Load thermography filter
                    flt_thermography = cam.filter_queue("Thermography")

                    buffer = cam.create_buffer() # Initialize buffer

                    # Grab a frame from the camera 100 times
                    for cnt in range(100):
                        cam.get_frame(buffer, XGetFrameFlags.XGF_Blocking)
                    
                    # Save the captured data
                    cam.save_data("output.xpng", XSaveDataFlags.XSD_SaveThermalInfo | XSaveDataFlags.XSD_Force16)

            except XenethAPIException as e:
                print(f"An error occurred: {e}")
        else:
            print("Initialization failed")
    except XenethAPIException as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        if cam.is_capturing:
            print("Stop capturing.")
            cam.stop_capture()
        if cam.is_initialized:
            print("Closing connection to camera.")
            cam.close()
            
if __name__ == "__main__":

    url = "cam://0"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
