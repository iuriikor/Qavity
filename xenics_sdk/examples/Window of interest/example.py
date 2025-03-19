"""
Window of interest example
"""
import sys
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

        if cam.is_initialized:
            print("Starting capture")
            cam.start_capture()

            if cam.is_capturing:
                buffer = cam.create_buffer()
                print(f"Current frame size is {cam.frame_size}, buffersize is {buffer.size}")

                # Make sure the camera is capable of setting a window of interest before continuing.
                if cam.get_property_value("CapWoiCount") is not None:
                    # Retrieve the current Woi values.
                    off_x = cam.get_property_value("OffsetX")
                    width = cam.get_property_value("Width")
                    off_y = cam.get_property_value("OffsetY")
                    height = cam.get_property_value("Height")

                    print(f"Current window of interest -> off_x: {off_x}, width: {width}, off_y: {off_y}, height: {height}")

                    # We set a window which is half the size of the current window.
                    cam.set_property_value("OffsetX", off_x)
                    cam.set_property_value("Width", width // 2)
                    cam.set_property_value("OffsetY", off_y)
                    cam.set_property_value("Height", height // 2)

                    # Retrieve the current Woi values.
                    off_x = cam.get_property_value("OffsetX")
                    width = cam.get_property_value("Width")
                    off_y = cam.get_property_value("OffsetY")
                    height = cam.get_property_value("Height")

                    print(f"Current window of interest after update -> off_x: {off_x}, width: {width}, off_y: {off_y}, height: {height}")
                    buffer = cam.create_buffer()
                    print(f"Current frame size is {cam.frame_size}, buffersize is {buffer.size}")

                    # We set a window to the max possible values
                    cam.set_property_value("OffsetX", 0)
                    cam.set_property_value("Width", cam.max_width)
                    cam.set_property_value("OffsetY", 0)
                    cam.set_property_value("Height", cam.max_height)

                    # Retrieve the current Woi values.
                    off_x = cam.get_property_value("OffsetX")
                    width = cam.get_property_value("Width")
                    off_y = cam.get_property_value("OffsetY")
                    height = cam.get_property_value("Height")

                    print(f"Current window of interest after update -> off_x: {off_x}, width: {width}, off_y: {off_y}, height: {height}")
                    buffer = cam.create_buffer()
                    print(f"Current frame size is {cam.frame_size}, buffersize is {buffer.size}")
                else:
                    print("The connected camera does not support windows of interest.")
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
