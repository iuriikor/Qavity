from xenics.xeneth import *
from xenics.xeneth.errors import XenethAPIException

from .Camera import Camera

import time
import cv2



class Xenics(Camera):
    def __init__(self, cam_id, framerate=10, exposure_ms=1):
        super().__init__(cam_id)
        self._buffer = None
        try:
            self._camera = XCamera()
            self._camera.open(cam_id)
            print(f"Opened connection to Xenics camera, ID {self._id}")
        except XenethAPIException as e:
            print(e.message)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            print(exception_traceback)
        self.close()
        return True if exception_type is None else False

    def initialize(self, framerate=10, exposure_ms=1):
        self.framerate = framerate
        try:
            self._buffer = self._camera.create_buffer()
            if self._camera.is_initialized:
                print("Camera Initialized")
            else:
                print("Initialization failed")
        except XenethAPIException as e:
            print(e.message)
        self.set_exposure_ms(exposure_ms)
        self._camera.start_capture()

    def get_frame(self):
        print('XENICS: getting frame')
        if self._buffer is not None:
            print('XENICS: buffer initialized correctly')
            if self._camera.get_frame(self._buffer, flags=XGetFrameFlags.XGF_Blocking):
                print('XENICS: image acquired and not None')
                return cv2.normalize(self._buffer.image_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            else:
                return None
        else:
            raise Exception("Xenics camera buffer not initialized")

    def close(self):
        if self._camera.is_capturing:
            try:
                print("Stop capturing")
                self._camera.stop_capture()
                print("Close Camera")
                self._camera.close()
            except XenethAPIException as e:
                print(e.message)

    def __del__(self):
        self.close()
        print(f"Camera {self._id} closed")

    def set_exposure_ms(self, exposure_ms):
        try:
            self._camera.set_property_value('ExposureTime', exposure_ms * 1e03)
            self.exposure_ms = exposure_ms
        except XenethAPIException as e:
            print(e.message)

    def get_exposure_ms(self):
        try:
            exposure_us = self._camera.get_property_value('ExposureTime')
            return exposure_us/1000.0
        except XenethAPIException as e:
            print(e.message)
            return None

    def stop_stream(self):
        """Stop streaming but keep the camera running"""
        print(f"Camera {self._id} stopping stream...")
        self.streamOn = False
        print(f"Camera {self._id} stream flag set to: {self.streamOn}")

    def start_stream(self):
        self.streamOn = True