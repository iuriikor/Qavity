"""
Working with pixelformats example
"""

import sys
from xenics.xeneth.capi.enums import XFilterMessage, XFrameType, XGetFrameFlags
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

        if not cam.is_initialized:
            print("Initialization failed")
            exit()

        for fmt in ["Mono8", "Mono16", "RGB8"]:
            
            print(f"Setting pixel format to '{fmt}'")
            cam.set_property_value("PixelFormat", fmt)
           
            # setting PixelFormat needs the cam to be closed and re-opened
            print("Closing and re-opening cam.")
            cam.close()
            cam.open(url)

            if not cam.is_initialized:
                print("Initialization failed")
                continue

            cam.start_capture()

            if cam.is_capturing:
                print(f"Frame Type: {cam.frame_type.name}, Frame Size: {cam.frame_size}")

                buffer = cam.create_buffer()

                print(f"Buffer shape {buffer.image_data.shape}, Buffer Type: {buffer.image_data.dtype}")
        
                for _ in range(100 ):
                    cam.get_frame(buffer, flags = XGetFrameFlags.XGF_Blocking )
                
                # for grayscale types, the pixel is a single value, for RGB type, the pixel contains an element for each channel
                print(buffer.data[0][0])
                cam.stop_capture()


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
