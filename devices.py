from controllers.cameras.ThorCam import ThorCam
from controllers.streamer import WebcamStreamer
from controllers.frequency_generators.Urukul import UrukulFrequencyGenerator

import os
import time

# Import ThorCam DLLs
os.add_dll_directory("C:\\Users\\CavLev\\Documents\\ControlGUI_Dash_v02_dash_mantine\\dll")
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
#
# CAMERAS
thorSDK = TLCameraSDK()
available_cameras = thorSDK.discover_available_cameras()
thorcam_1 = ThorCam(available_cameras[0], thorSDK)
thorcam_1.initialize(1, 10)
# thorcam_2 = ThorCam(available_cameras[1], thorSDK)
# thorcam_2.initialize(1, 100)
# CAMERA STREAMERS (sockets)
time.sleep(0.1)
streamer1 = WebcamStreamer(thorcam_1, "/stream1")
streamer1.stream()
# streamer2 = WebcamStreamer(thorcam_2, "/stream2")
# streamer2.stream()

# FREQUENCY GENERATORS
urukul_loading_params = {0 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 10.0, 'on': False},
                         1 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 10.0, 'on': False},
                         2 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 10.0, 'on': False},
                         3 : {'frequency': 300.0e03, 'amplitude': 0.5, 'attenuation': 10.0, 'on': False}}
urukul_loading_conn_params = {'ip_address': '10.34.16.100'}
urukul_loading = UrukulFrequencyGenerator(device_id='0',
                                          channel_params=urukul_loading_params,
                                          connection_params=urukul_loading_conn_params)

