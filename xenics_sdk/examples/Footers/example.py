"""
Footers example
"""
import sys
from xenics.xeneth.capi.enums import XFrameType, XGetFrameFlags
from xenics.xeneth.errors import XenethAPIException
from xenics.xeneth.xcamera import XCamera

# TODO: test with other camera's than 0xf090
def main(url):
    """
    Main program function.
    """
    cam = XCamera()

    try:
        # Open a connection to the first detected camera
        print("Opening connection to {url}")
        if not cam.open(url):
            raise XenethAPIException("Unable to open camera")

        # When the connection is initialised, ...
        if cam.is_initialized:
            # ... start capturing
            print("Start capturing.")
            cam.start_capture()
            if not cam.is_capturing:
                raise Exception("Could not start capturing")

            # Initialize the buffer so it fits the frame and footer
            buffer = cam.create_buffer()

            # ... grab a frame from the camera.
            print("Grabbing a frame.")

            if cam.get_frame(buffer, flags=XGetFrameFlags.XGF_Blocking | XGetFrameFlags.XGF_FetchPFF):
                # extract frame footer from buffer
                footer = buffer.extract_footer()

                print("\nSoftware footer contents:\n")
                print(f"     Structure length: {footer.len}")
                print(f"              Version: {footer.ver:X}")
                print(f"     Start of capture: {footer.soc}")
                print(f"    Time of reception: {footer.tft}")
                print(f"          Frame count: {footer.tfc}")
                print(f"        Filter marker: {footer.fltref}")
                print(f"  Hardware footer len: {footer.hfl}")
                print(f"  Hardware footer pid: {footer.pid:X}")

                if footer.pid == 0xf003: # GOBI class cameras. 
                    print("\nHardware footer contents:\n")
                    print(f"  Integration time: {footer.camera_footer.tint}")
                    print(f"          time low: {footer.camera_footer.timelo}")
                    print(f"         time high: {footer.camera_footer.timehi}")
                    print(f"   Die temperature: {footer.camera_footer.temp_die}")
                    print(f"               Tag: {footer.camera_footer.tag}")
                    print(f"      Image offset: {footer.camera_footer.image_offset}")
                    print(f"        Image gain: {footer.camera_footer.image_gain}")
                    print("\nStatus bits:\n")
                    print(f"      Trigger ext.: {footer.camera_footer.status.trig_ext}")

                elif footer.pid == 0xf040:   # ONCA class cameras
                    print("\Hardware footer contents:\n")
                    print(f"  Integration time: {footer.camera_footer.tint}")
                    print(f"          time low: {footer.camera_footer.timelo}")
                    print(f"         time high: {footer.camera_footer.timehi}")
                    print(f"   Die temperature: {footer.camera_footer.temp_die}")
                    print(f"  Case temperature: {footer.camera_footer.temp_case}")
                    print("\nStatus bits:\n")
                    print(f"      Trigger ext.: {footer.camera_footer.status.trig_ext}")
                    print(f"       Trigger cl.: {footer.camera_footer.status.trig_cl}")
                    print(f"      Trigger soft: {footer.camera_footer.status.trig_soft}")
                    print(f" Line cam fixed SH: {footer.camera_footer.status.linecam_fixedSH}")
                    print(f"Line cam SHB first: {footer.camera_footer.status.linecam_SHBfirst}")
                    print(f"      Filter wheel: {footer.camera_footer.status.filterwheel}")

                elif footer.pid == 0xf090:   # XCO class cameras
                    print("\nHardware footer contents:\n")
                    print(f"            Status: {footer.camera_footer.status}")
                    print(f"          Time low: {footer.camera_footer.timelo}")
                    print(f"         Time high: {footer.camera_footer.timehi}")
                    print(f"           Counter: {footer.camera_footer.counter}")
                    print(f"    Sample Counter: {footer.camera_footer.sample_counter}")
                    print(f"          Offset X: {footer.camera_footer.offset_x}")
                    print(f"          Offset Y: {footer.camera_footer.offset_y}")

                elif footer.pid == 0xf086:   # Manx class cameras
                    print("\nHardware footer contents:\n")
                    print(f"            Status: {footer.camera_footer.status}")
                    print(f"          Time low: {footer.camera_footer.timelo}")
                    print(f"         Time high: {footer.camera_footer.timehi}")
                    print(f"     Frame Counter: {footer.camera_footer.frame_counter}")
                    print("\nStatus bits:\n")
                    print(f"  First line index: {footer.camera_footer.status.first_line_index}")

            else:
                print("Unable to grab a frame.")

    except Exception as e:
        print(str(e))

    finally:
        # Cleanup.
        # When the camera is still capturing, ...
        if cam.is_capturing:
            # ... stop capturing.
            print("Stop capturing.")
            cam.stop_capture()

        # When the handle to the camera is still initialised ...
        if cam.is_initialized:
            print("Closing connection to camera.")
            cam.close()


if __name__ == "__main__":
        
    url = "cam://0?fg=none"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)