import os
import time
from matplotlib import pyplot as plt

# Import ThorCam DLLs
os.add_dll_directory("C:\\Users\\CavLev\\Documents\\Qavity\\dll")

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from cameras.ThorCam import ThorCam

try:
    # # CAMERAS
    thorSDK = TLCameraSDK()
    available_cameras = thorSDK.discover_available_cameras()
    thorcam_2 = ThorCam(available_cameras[1], thorSDK)
    thorcam_2.initialize(1, 20)

    img = thorcam_2.get_frame()

    plt.imshow(img)
    plt.show()

except Exception as e:
    print(e)

# finally:
#     # Cleanup
#     del thorcam_2
#     time.sleep(1)
#     del thorSDK