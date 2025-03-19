import os
from matplotlib import pyplot as plt

# Import ThorCam DLLs
os.add_dll_directory("C:\\Users\\CavLev\\Documents\\Qavity\\dll")

from cameras.Xenics import Xenics
from xenics.xeneth.errors import XenethAPIException



xenics_url = 'cam://0'
# Initialize the camera handle
xenics_cam = Xenics(xenics_url)
xenics_cam.initialize(framerate=1, exposure_ms = 0.01)
img = xenics_cam.get_frame()

plt.imshow(img)
plt.show()
