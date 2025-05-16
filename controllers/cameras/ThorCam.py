from .Camera import Camera
import cv2
import time

class ThorCam(Camera):
    def __init__(self, cam_id, sdk, **kwargs):
        super().__init__(cam_id)
        self._sdk = sdk
        self._current_frame = None  # Instance variable to hold the current frame
        self._image_buffer = None  # Instance variable to hold the image buffer
        print(f"Initialized camera, ID {self._id}")
        
    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            print(exception_traceback)
        self.close()
        return True if exception_type is None else False

    def initialize(self, framerate=10, exposure_ms=1, polling_timeout_ms=1000, **kwargs):
        # First unwrap any additional camera properties
        self.rotate_img = kwargs.get("rotate_img", False)
        self.roi_hor = kwargs.get("roi_hor", None)
        self.roi_ver = kwargs.get("roi_ver", None)
        # Then initialize camera
        camera = self._sdk.open_camera(self._id)
        time.sleep(1) # Let the camera connect and start properly
        self._camera = camera
        self._camera.frames_per_trigger_zero_for_unlimited = 0
        self.set_exposure_ms(exposure_ms)
        self.set_timeout(polling_timeout_ms)
        self.framerate = framerate
        self._camera.arm(2)
        self._camera.issue_software_trigger()

    def get_frame(self):
        # print("Acquiring frame")
        self._current_frame = self._camera.get_pending_frame_or_null()
        # print("Frame acquired")
        if self._current_frame is not None:
            self._image_buffer = self._current_frame.image_buffer
            # print("CAMERA SIDE: FRAME IS NOT NONE")
            if self.rotate_img:
                return cv2.rotate(self._image_buffer, cv2.ROTATE_90_CLOCKWISE)
            else:
                return self._image_buffer
        else:
            # print("CAMERA SIDE: FRAME IS NONE")
            return None

    def close(self):
        self._camera.disarm()
        self._camera.dispose()
        
    def __del__(self):
        self._camera.disarm()
        self._camera.dispose()
        print(f"Camera {self._id} closed")

    def set_exposure_ms(self, exposure):
        self._camera.exposure_time_us = int(exposure*1000)

    def get_exposure_ms(self):
        return self._camera.exposure_time_us/1000.0

    def set_timeout(self, timeout):
        self._camera.image_poll_timeout_ms = timeout

    def stop_stream(self):
        """Stop streaming but keep the camera running"""
        print(f"Camera {self._id} stopping stream...")
        self.streamOn = False
        print(f"Camera {self._id} stream flag set to: {self.streamOn}")

    def start_stream(self):
        self.streamOn = True



