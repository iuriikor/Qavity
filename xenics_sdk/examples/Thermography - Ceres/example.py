"""
Ceres thermography example

The script assumes that a radiometric calibration is loaded in the selected image correction source on board of the camera
"""

import math
import sys
from xenics.xeneth.capi.enums import XFrameType, XGetFrameFlags
from xenics.xeneth.errors import XenethAPIException

from xenics.xeneth.xcamera import XCamera

# Function declarations
def temperature_in_temperature_mode(adu, maximal_adu, minimal_temperature, maximal_temperature):
    # The temperature is computed using linear interpolation between the Selection minimal and the Selection maximal temperature.
    fraction = adu / maximal_adu
    return minimal_temperature + fraction * (maximal_temperature - minimal_temperature)

def temperature_in_radiance_mode(adu, s1, s2, s3, s4, emissivity, ambient_temperature):
    # The temperature is computed using the function Rad_BB = S1 + S2 * (exp(S3/(Temperature + S4)) - 1)^(-1)
    rad = adu

    # If the object is not a perfect blackbody we take into account the emissivity and the ambient temperature
    # according to the following rule: Rad_object = emissivity * Rad_BB + (1 - emissivity) * Rad_ambient.
    if emissivity < 1.0:
        ambient_adu = temp_to_rad(ambient_temperature, s1, s2, s3, s4)
        rad -= (1 - emissivity) * ambient_adu
        rad /= emissivity

    return temp_from_rad(rad, s1, s2, s3, s4)


# TODO: check this for ceres cam
def temp_to_rad(temperature, s1, s2, s3, s4):
    # Rad_BB = S1 + S2 * (exp(S3/(Temperature + S4)) - 1)^(-1)
    ret = math.exp(s3 / (temperature + s4)) - 1
    ret = s1 + (s2 / ret)

    return ret


# TODO: check this for ceres cam
def temp_from_rad(radiance, s1, s2, s3, s4):
    ret = radiance - s1
    ret = s2 / ret
    ret += 1

    if ret > 0:
        ret = math.log(ret)
        ret = s3 / ret
        ret -= s4
        return ret
    else:
        return 0

    

def main(url):
    # Variables

    max_adu = 0
    width = 0
    height = 0

    # Radiometry parameters
    emissivity = 0.95  # emissivity of the observed object
    ambient_temp = 300  # temperature near the observed object

    # Create an instance of the XCamera class
    cam = XCamera()

    try:
        # Open a connection to the camera specified by url
        print("Opening connection to {url}")
        cam.open(url)

        # When the connection is initialized, ...
        if cam.is_initialized:
            
            buffer = cam.create_buffer(XFrameType.FT_NATIVE)
            max_adu = cam.max_value
            width = cam.width
            height = cam.height

            cam.set_property_value('ThermographyEnable', 1)

            # Verify emissivity.
            if emissivity < 0.1: emissivity = 0.1
            if emissivity > 1.0: emissivity = 1.0

            # Temperature conversion in temperature mode.
            cam.set_property_value('ThermographyMode', 'Temperature')
            print("\nTemperature mode.\n")
            cam.set_property_value('ThermographyTemperatureEmissivity', emissivity)
            cam.set_property_value('ThermographyTemperatureAmbientTemperature', ambient_temp)

            mintemp = cam.get_property_value('ThermographyTemperatureSelectionMinimalTemperature')
            maxtemp = cam.get_property_value('ThermographyTemperatureSelectionMaximalTemperature')

            # .. start capturing.
            print("Start capturing.\n")
            
            cam.start_capture()
            
            for _ in range(100):
                cam.get_frame(buffer, XGetFrameFlags.XGF_Blocking)
                adu = buffer.image_data.flat[width // 2 + (height // 2 * width)]
                temperature = temperature_in_temperature_mode(adu, max_adu, mintemp, maxtemp)
                print(f"Temperature at center: {temperature:.1f} Kelvin.")

           
            print("Stop capturing.\n")
            cam.stop_capture()

            # Temperature conversion in radiance mode.
            cam.set_property_value('ThermographyMode', 'Radiometric') 
            print("\nRadiance mode.\n")
            mintemp = cam.get_property_value('ThermographyTemperatureMinimalTemperature')
            maxtemp = cam.get_property_value('ThermographyTemperatureMaximalTemperature')

            S1 = cam.get_property_value('ThermographyRadiometryP1')
            S2 = cam.get_property_value('ThermographyRadiometryP2')
            S3 = cam.get_property_value('ThermographyRadiometryP3')
            S4 = cam.get_property_value('ThermographyRadiometryP4')

            # .. start capturing.
            print("Start capturing.\n")
            cam.start_capture()
                
            for _ in range(100):
                cam.get_frame(buffer, XGetFrameFlags.XGF_Blocking)
                adu = buffer.image_data.flat[width // 2 + (height // 2 * width)]
                temperature = temperature_in_radiance_mode(adu, S1, S2, S3, S4, emissivity, ambient_temp)
                if temperature < mintemp or temperature > maxtemp:
                    print(f"Temperature at center: {temperature:.1f} Kelvin. This is out of the calibration range.")
                else:
                    print(f"Temperature at center: {temperature:.1f} Kelvin.")


            print("Stop capturing.\n")
            cam.stop_capture()

        else:
            print("Could not initialise connection")
    except XenethAPIException as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        if cam.is_capturing:
            print("Stop capturing.")
            cam.stop_capture()
        if cam.is_initialized:
            print("Closing connection to camera.")
            cam.close()

if __name__ == "__main__":

    url = "cam://0"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    main(url)
