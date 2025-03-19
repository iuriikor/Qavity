"""
Loading files example
"""

import sys
import os
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

        pack = os.path.join(os.path.dirname(__file__), "pack.xca")
        property_name = "FileAccessCorrectionFile"

        # When the connection is initialised, ...
        if cam.is_initialized:
            print(f"Connection to '{url}' initialised.")

            # This example is tested using a Bobcat-640 (0xF035) camera.
            try:
                print(f"Uploading '{pack}' to '{property_name}': ", end="")
                cam.set_property_value(property_name, pack)
                print("OK")
            except XenethAPIException as e:
                print(f"Error when uploading the pack: {e}")

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
