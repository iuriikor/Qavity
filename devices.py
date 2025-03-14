from controllers.cameras.ThorCam import ThorCam
from controllers.frequency_generators.Urukul import UrukulFrequencyGenerator
import os

# Import ThorCam DLLs
os.add_dll_directory("C:\\Users\\CavLev\\Documents\\ControlGUI_Dash_v02_dash_mantine\\dll")
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK


thorSDK = TLCameraSDK()
available_cameras = thorSDK.discover_available_cameras()
thorcam_1 = ThorCam(available_cameras[0], thorSDK)
thorcam_1.initialize(10, 10)
thorcam_2 = ThorCam(available_cameras[1], thorSDK)
thorcam_2.initialize(1, 100)

