import os
import time

# Import ThorCam DLLs
os.add_dll_directory("C:\\Users\\CavLev\\Documents\\Qavity\\dll")
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

from controllers.cameras.ThorCam import ThorCam
from controllers.cameras.Xenics import Xenics
from controllers.streamer import WebcamStreamer
from controllers.frequency_generators.Urukul import UrukulFrequencyGenerator

def save_as_bin(data, file_path):
    """
    Save data as binary file
    """
    with open(file_path, 'wb') as f:
        f.write(data)

#
# # CAMERAS
# thorSDK = TLCameraSDK()
# available_cameras = thorSDK.discover_available_cameras()
# thorcam_1 = ThorCam(available_cameras[0], thorSDK)
# thorcam_1.initialize(1, 100)
# thorcam_2 = ThorCam(available_cameras[1], thorSDK)
# thorcam_2.initialize(1, 20)

xenics_url = 'cam://0'
xenics_cam = Xenics(xenics_url)
xenics_cam.initialize(1, 0.01)
# CAMERA STREAMERS (sockets)
time.sleep(0.1)
# streamer1 = WebcamStreamer(thorcam_1, "/stream1")
# streamer2 = WebcamStreamer(thorcam_2, "/stream2")
streamer3 = WebcamStreamer(xenics_cam, "/stream3")

# FREQUENCY GENERATORS
urukul_loading_params = {0 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 10.0, 'on': False},
                         1 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 10.0, 'on': False},
                         2 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 10.0, 'on': False},
                         3 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 10.0, 'on': False}}
urukul_loading_conn_params = {'ip_address': '10.34.16.100'}
urukul_loading = UrukulFrequencyGenerator(device_id='0',
                                          channel_params=urukul_loading_params,
                                          connection_params=urukul_loading_conn_params)

