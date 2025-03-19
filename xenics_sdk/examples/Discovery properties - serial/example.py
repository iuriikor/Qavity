"""
Device discovery properties example.
"""

# import all from high level API
from xenics.xeneth.discovery import get_property_value, set_property_value
from xenics.xeneth.errors import XenethAPIException

def main():
    """
    Main program function
    """
    com_low = 0
    com_high = 0

    try:
        print("Reading default discovery properties")
        com_low = get_property_value("COMPortLow")
        com_high = get_property_value("COMPortHigh")

        print(f"The current default values are {com_low} to {com_high}\n")
    except XenethAPIException as e:
        print(f"An issue occurred while trying to retrieve the default discovery properties ({e.error_code}).\n")


    try:
        print("Writing new discovery properties")
        set_property_value("COMPortLow", 128)
        set_property_value("COMPortHigh", 255)
    except XenethAPIException as e:
        print(f"An issue occurred while trying to set the new discovery properties ({e.error_code}).\n")


    try:
        print("Reading new discovery properties")
        com_low = get_property_value("COMPortLow")
        com_high = get_property_value("COMPortHigh")

        print(f"The new values are {com_low} to {com_high}\n")
    except XenethAPIException as e:
        print(f"An issue occurred while trying to retrieve the new discovery properties ({e.error_code}).\n")


if __name__ == '__main__':
    main()
