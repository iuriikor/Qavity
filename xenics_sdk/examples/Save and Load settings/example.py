"""
Save and load settings example
"""

import sys
from xenics.xeneth.xcamera import XCamera
from xenics.xeneth.errors import XenethAPIException

def main(url):
    # Create an instance of the XCamera class
    cam = XCamera()

    try:
        # Open a connection to the camera specified by url
        print("Opening connection to {url}")
        cam.open(url)

        # When the connection is initialized, ...
        if cam.is_initialized:
            settings = "settings.xcf"
            newint = 32

            # Save settings
            print("Saving settings.")
            cam.save_settings(settings)

            # Change a property
            oldint = cam.get_property_value('IntegrationTime')
            cam.set_property_value('IntegrationTime', newint)
            print(f"- Saved IntegrationTime value: {oldint}\n- New IntegrationTime value: {newint}")

            # Load settings.
            print("Load settings.")
            cam.load_settings(settings)

            # Verify new value..
            oldint = cam.get_property_value('IntegrationTime')
            print(f"- Loaded IntegrationTime value: {oldint}")

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
    
    url = "cam://0?fg=none"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
