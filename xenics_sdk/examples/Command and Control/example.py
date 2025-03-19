"""
Camera connection and property retrieval example
"""

import sys
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera

def main(url):
    """
    Main program function.
    """
    # Variables
    cam = XCamera()
    try:
        print(f"Opening connection to {url}")
        cam.open(url)

        # When the connection is initialised, ...
        if cam.is_initialized:
            pid = cam.get_property_value("_CAM_PID")
            ser = cam.get_property_value("_CAM_SER")
            exposure_time = cam.get_property_value("ExposureTime")

            # Output the product id and serial.
            print(f"Controlling camera with PID: 0x{int(pid):X}, SER: {ser}, ExposureTime: {exposure_time}")

            # A call to the getframe functions will not return an error, but the image will be black since no thread is running to grab images.
        else:
            print("Initialization failed")

    except XenethAPIException as e:
        print(f"An error occurred: {e}")

    finally:
        # Cleanup.

        # When the handle to the camera is still initialised ...
        if cam.is_initialized:
            print("Closing connection to camera.")
            cam.close()

if __name__ == "__main__":
        
    url = "cam://0?fg=none"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
