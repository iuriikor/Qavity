"""
filter_parameters.py
"""

import sys
from xenics.xeneth.capi.enums import XFilterMessage
from xenics.xeneth.errors import XenethAPIException, XenethException
from xenics.xeneth.xcamera import XCamera


def main(url):
    """
    Main function.
    """

    flt_handle = 0  # Handle to an image filter.
    
    # Create an instance of the camera
    cam = XCamera()
    
    try:
        # Open the camera
        cam.open(url)

        # When the connection is initialised...
        if cam.is_initialized:
            flt_handle = cam.filter_queue("Averaging")

            if cam.is_filter_running(flt_handle):
                
                print("Filter up and running.")

                # The averaging filter has 1 parameter, NumFrames, which is an integer value of the number of frames to average.
                # The parameter must be in ASCII format. So the integer char value '2' is represented as decimal value 50.
                value = cam.filter_get_parameter(flt_handle, "NumFrames")

                # Set the value to "5"
                cam.filter_set_parameter(flt_handle, "NumFrames", "5")

                print(f"Got value {value} from NumFrames, set to {'5'}.")

                # To export every setting at once, the RecvStream with Serialise message can be used. This allows to discover the parameters of a filter.
                try:
                    result = cam.filter_recv_stream(flt_handle, XFilterMessage.XMsgSerialise)
                
                    print(result)
                except XenethAPIException as e:
                    print(f"Deserialize command failed. ({e.message})")

                # Removing the image filters from the stack
                cam.rem_image_filter(flt_handle)
            else:
                print("Failed queueing autogain or gamma filter.")
        else:
            print("Initialization failed")

    except XenethException as e:
        print(e)
    finally:
        # When the handle to the camera is still initialised...
        if cam.is_initialized:
            print("Closing connection to camera.")
            cam.close()

    return 0

if __name__ == "__main__":
        
    url = "cam://0"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
