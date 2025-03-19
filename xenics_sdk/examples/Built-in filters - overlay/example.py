import ctypes
import sys

from xenics.xeneth.capi.enums import XFilterMessage, XFrameType, XGetFrameFlags, ColourMode
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera


def save_as_bin(data, file_path):
    """
    Save data as binary file
    """
    with open(file_path, 'wb') as f:
        f.write(data)

    # Result can viewed with ImageJ: File > Import > Raw > 32-bit ABGR, big endian 

def main(url):
    """
    Main Program function
    """
    cam = XCamera()

    try:
        print("Open camera")
        cam.open(url)
        buffer = cam.create_buffer(frame_type=XFrameType.FT_32_BPP_BGRA)

        if cam.is_initialized:
            # Set colour mode
            cam.colour_mode = ColourMode.ColourMode_16

            # Queue overlay filter
            overlay_filter = cam.filter_queue("Overlay")

            if cam.is_filter_running(overlay_filter):

                result = cam.filter_recv_stream(overlay_filter, XFilterMessage.XMsgSerialise)
                print(result)
                
                print("Starting capture")
                cam.start_capture()
                
                # Write some text to the overlay
                # At the moment, we have a bug, throwing error 10000
                try: 
                    cam.filter_set_parameter(overlay_filter, "OverlayImageEnable", "False") 
                except: pass
                try: 
                    cam.filter_set_parameter(overlay_filter, "OverlayTextEnable", "True") 
                except: pass
                try: 
                    cam.filter_set_parameter(overlay_filter, "OverlayTextOffsetX", "0")
                except: pass
                try: 
                    cam.filter_set_parameter(overlay_filter, "OverlayTextOffsetY", "0")
                except: pass
                try: 
                    cam.filter_set_parameter(overlay_filter, "OverlayTextText", "qwerty")
                except: pass

                result = cam.filter_recv_stream(overlay_filter, XFilterMessage.XMsgSerialise)
                print(result)
                
                if cam.is_capturing:
                    print("Grabbing a frame")

                    if cam.get_frame(buffer, flags=XGetFrameFlags.XGF_Blocking):
                        # Save the frame as binary
                        save_as_bin(buffer.image_data, "image_with_overlay.bin")

                    else:
                        print("Problem while fetching frame")
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
