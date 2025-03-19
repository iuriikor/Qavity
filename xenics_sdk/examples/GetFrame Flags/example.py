# import all from high level API
import sys
from xenics.xeneth.capi.enums import XGetFrameFlags
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera

def main(url):
    """
    Main Program function
    """
    cam = XCamera()

    try:
        print("Open camera")
        cam.open(url)
        buffer = cam.create_buffer()

        if cam.is_initialized:

            print("Starting capture")
            cam.start_capture()


            # Grabbing 5 frames in non-blocking mode
            print("\nGrabbing 5 frames in non-blocking mode (default)\n")

            for i in range(5):
                try:
                    print(f"Grabbing frame {i}")

                    while not cam.get_frame(buffer):
                        # Do some idle work here
                        pass

                    print("Image Captured.")
                except XenethAPIException as e:
                    print(e.message)


            # Grabbing 5 frames in blocking mode
            print("\n\nGrabbing 5 frames in blocking mode\n")

            for i in range(5):
                try:
                    print(f"Grabbing frame {i}")

                    if cam.get_frame(buffer, flags=XGetFrameFlags.XGF_Blocking):
                        print("Image Captured.")

                except XenethAPIException as e:
                    print(e.message)

            # Grabbing 5 frames in blocking and no conversion mode
            print("\n\nGrabbing 5 frames in blocking and no conversion mode\n")

            for i in range(5):
                try:
                    print(f"Grabbing frame {i}")

                    while not cam.get_frame(buffer, flags=XGetFrameFlags.XGF_Blocking | XGetFrameFlags.XGF_NoConversion):
                        # do some idle work here
                        pass

                    print("Image Captured.")

                except XenethAPIException as e:
                    print(e.message)

        else:
            print("Initialization failed")
    except XenethAPIException as e:
        print(e.message)


    # Cleanup
    if cam.is_capturing:
        try:
            print("Stop capturing")
            cam.stop_capture()

            print("Close Camera")
            cam.close()

        except XenethAPIException as e:
            print(e.message)


if __name__ == '__main__':
        
    url = "cam://0"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)