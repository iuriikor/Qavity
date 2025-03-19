"""
Enumerate properties example.
"""
import sys
from xenics.xeneth import XCamera
from xenics.xeneth.capi.enums import XPropType
from xenics.xeneth.errors import XenethAPIException

def main(url):
    """
    Main program function
    """
    # Initialize the camera handle
    cam = XCamera()

    try:
        # Open a connection to the first detected camera by using connection string cam://0
        # Note the fg parameter that is passed in the query part of the connection string.
        print("Opening connection to {url}")
        cam.open(url)

        # When the connection is initialised, ...
        if cam.is_initialized:
            property_count = cam.get_property_count()
            # Iterate over each property and output details such as name, type, value
            for i in range(property_count):
                property_name = cam.get_property_name(i)
                property_category = cam.get_property_category(property_name)
                property_type = cam.get_property_type(property_name)
                property_range = cam.get_property_range(property_name)
                property_unit = cam.get_property_unit(property_name)

                print(f"Property[{i}]    Category: {property_category}")
                print(f"Property[{i}]        Name: {property_name}")
                print(f"Property[{i}]       Flags: {str(property_type)}")

                # The following output depends on the property type.
                if property_type & XPropType.XType_Base_Mask == XPropType.XType_Base_Number:
                    value = cam.get_property_value(property_name)

                    print(f"Property[{i}]        Type: Number")
                    print(f"Property[{i}]       Range: {property_range}")
                    print(f"Property[{i}]        Unit: {property_unit}")
                    print(f"Property[{i}]        Value: {value}")

                elif property_type & XPropType.XType_Base_Mask == XPropType.XType_Base_Enum:
                    value = cam.get_property_value(property_name)

                    print(f"Property[{i}]        Type: Enum")
                    print(f"Property[{i}]       Range: {property_range}")
                    print(f"Property[{i}]       Value: {value}")

                elif property_type & XPropType.XType_Base_Mask == XPropType.XType_Base_Bool:
                    value = cam.get_property_value(property_name)

                    print(f"Property[{i}]        Type: Bool")
                    print(f"Property[{i}]       Value: {value}")

                elif property_type & XPropType.XType_Base_Mask == XPropType.XType_Base_Blob:
                    print(f"Property[{i}]        Type: Blob")

                elif property_type & XPropType.XType_Base_Mask == XPropType.XType_Base_Action:
                    print(f"Property[{i}]        Type: Action")


                elif property_type & XPropType.XType_Base_Mask == XPropType.XType_Base_String:
                    value = cam.get_property_value(property_name)

                    print(f"Property[{i}]        Type: String")
                    print(f"Property[{i}]       Value: {value}")

                print()

        else:
            print("Initialization failed")

    except XenethAPIException as e:
        print(e.message)


    finally:
        # Cleanup.
        # When the handle to the camera is still initialised ...
        if cam.is_initialized:
            print("Closing connection to camera.")
            cam.close()


if __name__ == "__main__":
        
    url = "cam://0?fg=none"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
