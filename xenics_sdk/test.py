"""
Pixel conversion and ColourMode example.
"""

# import all from high level API
import os
import sys
from xenics.xeneth.capi.enums import ColourMode, XFrameType, XGetFrameFlags
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera
from PIL import Image

def main(url):
    """
    Main Program function
    """
    profilepath = os.path.join(os.path.dirname(__file__), "colorprofile.png")

    cam = XCamera()

    # Open a connection to the first detected camera by using connection string in url argument
    print(f"Opening connection to {url}")
    cam.open(url)

    # When the connection is initialised, ...
    if cam.is_initialized:
        # ... start capturing
        print("Start capturing.")
        try:
            cam.start_capture()
        except XenethAPIException as e:
            print(f"Could not start capturing, errorCode: {e}")

        if cam.is_capturing:  # When the camera is capturing ...
            
            #cam.load_colour_profile(profilepath)
            #cam.colour_mode = ColourMode.ColourMode_Profile

            # ... grab a frame from the camera - FT_32_BPP_RGBA
            print("Grabbing a frame - FT_32_BPP_RGBA.")
            buffer = cam.create_buffer(XFrameType.FT_32_BPP_RGB)
            try:
                cam.get_frame(buffer, XFrameType.FT_32_BPP_RGB, XGetFrameFlags.XGF_Blocking )
                r = buffer.image_data[0][0][0]
                g = buffer.image_data[0][0][1]
                b = buffer.image_data[0][0][2]
                #a = buffer.image_data[0][0][3]

                img = Image.fromarray(buffer.image_data, "RGB")
                img.save("img1.png")

                print(f"Pixel value: r = {r}, g = {g}, b = {b}")
            except XenethAPIException as e:
                print(e.message)

            # ... grab a frame from the camera - FT_32_BPP_BGRA
            print("Grabbing a frame - FT_32_BPP_BGRA.")
            buffer = cam.create_buffer(XFrameType.FT_32_BPP_BGR)
            try:
                cam.get_frame(buffer, XFrameType.FT_32_BPP_BGR, XGetFrameFlags.XGF_Blocking)
                b = buffer.image_data[0][0][0]
                g = buffer.image_data[0][0][1]
                r = buffer.image_data[0][0][2]
                #a = buffer.image_data[0][0][3]

                img = Image.fromarray(buffer.image_data, "RGB")
                img.save("img2.png")
                print(f"Pixel value: r = {r}, g = {g}, b = {b}")
            except XenethAPIException as e:
                print(e.message)

    else:
        print("Initialization failed")

    # Cleanup.
    if cam.is_capturing:  # When the camera is still capturing ...
        # ... stop capturing.
        print("Stop capturing.")
        cam.stop_capture()

    # When the handle to the camera is still initialised ...
    if cam.is_initialized:
        # .. close the connection.
        print("Closing connection to camera.")
        cam.close()

if __name__ == '__main__':
    
    url = "cam://0"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
