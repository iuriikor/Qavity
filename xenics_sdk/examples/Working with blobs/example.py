"""
Working with blobs example
"""

import sys
import os
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera

def main(url):
    """
    Main program function.
    """
    # Variables
    cam = XCamera()
    try:
        print("Opening connection to {url}")
        cam.open(url)

        # When the connection is initialised, ...
        if cam.is_initialized:
            pid = cam.get_property_value("_CAM_PID")
            print(f"Connected to a 0x{int(pid):X} camera")

            # This example is tested using a Bobcat-640 (0xF035) camera.
            if pid == 0xF035:
                file_path = os.path.join(os.path.dirname(__file__), "pack.xca")

                # Open file in mode binary read!
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                    
                        try:
                            # Upload the blob.
                            print("Uploading binary Blob to camera.")

                            # Fill buffer with file data.
                            buffer = file.read()
                            cam.set_property_value("FileAccessCorrectionFile", buffer)
                            print("Upload complete!")
                        except XenethAPIException as e:
                            print(f"An error state was returned when loading the blob to the camera, code: {e}")

                        
                        try:
                            print("Uploading Blob to camera using file path.")
                            cam.set_property_value("FileAccessCorrectionFile", file_path)
                            print("Upload complete!")
                        except XenethAPIException as e:
                            print(f"An error state was returned when loading the blob to the camera, code: {e}")

                else:
                    print(f"{file_path} not found. Make sure you have a calibration pack for camera with PID 0x{int(pid):X}.")

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
        
    url = "cam://0"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
