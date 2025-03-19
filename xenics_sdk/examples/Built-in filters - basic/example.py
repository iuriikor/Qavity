"""
Built-in filters example
"""

import sys
from xenics.xeneth.errors import XenethException
from xenics.xeneth.xcamera import XCamera

def main(url):
    """
    Main program function.
    """

    try:
        # Open a connection to the first detected camera by using connection string cam://0
        print(f"Opening connection to {url}")
        cam = XCamera()
        cam.open(url)

        # When the connection is initialised...
        if cam.is_initialized:

            # Retrieve the filter list.
            filterlist = cam.filter_get_list()
            print(f"Filters currently available:\n{' - '.join(filterlist)}")

            flt_auto_gain = cam.filter_queue("AutoOffsetAndGain")
            flt_matrix = cam.filter_queue("Matrix")
            flt_averaging = cam.filter_queue("Averaging")

            if (cam.is_filter_running(flt_auto_gain) and
                cam.is_filter_running(flt_matrix) and
                cam.is_filter_running(flt_averaging)):
                print("Filters up and running.")

                # Current filter stack: AutoOffsetAndGain, Matrix, Averaging

                # Set the Averaging filter at the top of the filter stack.
                cam.pri_image_filter(flt_averaging, 0)

                # Current filter stack: Averaging, AutoOffsetAndGain, Matrix

                # Set the Averaging filter in front of the Matrix filter.
                cam.pri_image_filter(flt_averaging, -flt_matrix)

                # Current filter stack: AutoOffsetAndGain, Averaging, Matrix

                # Set the AutoOffsetAndGain filter behind the Averaging filter.
                cam.pri_image_filter(flt_auto_gain, flt_averaging)

                # Current filter stack: Averaging, AutoOffsetAndGain, Matrix

                # Removing the image filters from the stack
                cam.rem_image_filter(flt_averaging)
                cam.rem_image_filter(flt_auto_gain)
                cam.rem_image_filter(flt_matrix)
            else:
                print("Failed queueing AutoOffsetAndGain, averaging or matrix filter.")
        else:
            print("Initialization failed")
    except XenethException as e:
        print(f"An error occurred: {e.message}")

    finally:
        # Cleanup.

        # When the handle to the camera is still initialised...
        if cam.is_initialized:
            print("Closing connection to camera.")
            cam.close()

if __name__ == "__main__":
        
    url = "cam://0"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)