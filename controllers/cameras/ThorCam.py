from .Camera import Camera
import time

class ThorCam(Camera):
    def __init__(self, cam_id, sdk):
        super().__init__(cam_id)
        self._sdk = sdk
        print(f"Initialized camera, ID {self._id}")
        
    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            print(exception_traceback)
        self.close()
        return True if exception_type is None else False

    def initialize(self, framerate=10, exposure_ms=1, polling_timeout_ms=1000):
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
        frame = self._camera.get_pending_frame_or_null()
        # print("Frame acquired")
        if frame is not None:
            # print("CAMERA SIDE: FRAME IS NOT NONE")
            return frame.image_buffer
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
        self._camera.exposure_time_us = exposure*1000

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



