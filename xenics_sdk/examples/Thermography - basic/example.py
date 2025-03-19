"""
Basic thermography example
"""

import os
import sys
from xenics.xeneth.capi.enums import XFrameType, XGetFrameFlags
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera

def main(url):

    # Calibration pack path - specific to the camera
    # This example is created using the Gobi+ 640 GigE (pid: 0xF229) camera.
    # Please make sure to use a calibration file for the camera you are using
    packname = os.path.join(os.path.dirname(__file__), "pack.xca")

    # Create an XCamera instance
    cam = XCamera()

    try:
        # Open a connection to the camera
        print(f"Opening connection to '{url}'")
        cam.open(url)

        # Check if the connection is initialized
        if cam.is_initialized:
            try:
                # Load the calibration pack
                cam.load_calibration(packname, 0)
                
                # Queue the thermography filter
                flt_thermography = cam.filter_queue("Thermography", "celsius")

                # Check if the filter was initialized successfully
                if flt_thermography > 0:

                    # Start capturing frames
                    print("Start capturing.")
                    cam.start_capture()

                    # Create a buffer for the incoming frames
                    buffer = cam.create_buffer(XFrameType.FT_16_BPP_GRAY)

                    # Check if the camera is capturing frames
                    if cam.is_capturing:
                        # Get the first frame
                        cam.get_frame(buffer, XGetFrameFlags.XGF_Blocking)
                        
                        # Build the lookup table
                        lut = [cam.filter_adu_to_temperature(flt_thermography, x) for x in range(cam.max_value+1)]
                        
                        while True:
                            cam.get_frame(buffer, XGetFrameFlags.XGF_Blocking)
                            
                            width = cam.width
                            height = cam.height
                            
                            # Print the temperature at the center of the frame
                            print(f"Temperature at center: {lut[buffer.image_data.flat[width//2 + (height//2)*width]]:.2f} degrees Celsius")
                else:
                    print("Could not start thermography filter, closing connection.")
            except XenethAPIException as e:
                print(f"Could not load calibration pack '{packname}', closing connection: {e}")
        else:
            print("Initialization failed")

    except XenethAPIException as e:
        print(f"An error occurred: {e}")

    finally:
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
