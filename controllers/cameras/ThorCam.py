from .Camera import Camera
import cv2
import time
import os
from datetime import datetime

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
        self.roi_x_tl = kwargs.get("roi_x_tl", None)
        self.roi_y_tl = kwargs.get("roi_y_tl", None)
        self.roi_x_br = kwargs.get("roi_x_br", None)
        self.roi_y_br = kwargs.get("roi_y_br", None)
        # Then initialize camera
        camera = self._sdk.open_camera(self._id)
        time.sleep(1) # Let the camera connect and start properly
        self._camera = camera
        self._camera.frames_per_trigger_zero_for_unlimited = 0
        # Set camera acquisition properties
        self.set_exposure_ms(exposure_ms)
        self.set_timeout(polling_timeout_ms)
        self.framerate = framerate
        # Get sensor size
        self.sensor_width = self._camera.sensor_width_pixels
        self.sensor_height = self._camera.sensor_height_pixels
        # Arm camera for acquisition
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

    def set_ROI(self, upper_left_x_pixels, upper_left_y_pixels,
                lower_right_x_pixels, lower_right_y_pixels):
        """
        Sets ROI of the camera using 2 pairs or X-Y pixel coordintates, top left and bottom right.
        THIS METHOD NEEDS THAT THE VALUES ARE RANGE CHECKED BEFORE BEING PASSED.

        :param upper_left_x_pixels: x-coordinate, top left
        :param upper_left_y_pixels: y-coordinate, top left
        :param lower_right_x_pixels: x-coordinate, bottom right
        :param lower_right_y_pixels: y-coordinate, bottom right
        :return: None
        """
        self.roi_x_tl = int(upper_left_x_pixels)
        self.roi_y_tl = int(upper_left_y_pixels)
        self.roi_x_br = int(lower_right_x_pixels)
        self.roi_y_br = int(lower_right_y_pixels)
        try:
            # Need to disarm before setting ROI
            self._camera.disarm()
            self._camera.roi = (self.roi_x_tl, self.roi_y_tl, self.roi_x_br, self.roi_y_br)
            # Arm again
            self._camera.arm(2)
            self._camera.issue_software_trigger()
        except Exception as e:
            print(e)

    def get_ROI(self):
        return (self.roi_x_tl, self.roi_y_tl, self.roi_x_br, self.roi_y_br)

    def set_timeout(self, timeout):
        self._camera.image_poll_timeout_ms = timeout

    def stop_stream(self):
        """Stop streaming but keep the camera running"""
        print(f"Camera {self._id} stopping stream...")
        self.streamOn = False
        print(f"Camera {self._id} stream flag set to: {self.streamOn}")

    def start_stream(self):
        self.streamOn = True

    def save_image(self, folder_path, image_name):
        """
        Save current camera frame as 16-bit PNG with timestamp prefix.
        Always saves as 16-bit to preserve maximum dynamic range.
        
        Args:
            folder_path (str): Directory path to save the image
            image_name (str): Base name for the image file (without extension)
            
        Returns:
            str: Full path of saved file if successful, None if failed
        """
        # Get current frame
        frame_to_save = None
        
        # First try to use existing current frame
        if self._image_buffer is not None:
            frame_to_save = self._image_buffer
            print(f"Camera {self._id}: Using existing frame for save")
        else:
            # Try to get a new frame
            print(f"Camera {self._id}: Getting new frame for save")
            frame_to_save = self.get_frame()
        
        # Check if we have a valid frame
        if frame_to_save is None:
            print(f"Camera {self._id}: No frame available to save")
            return None
        
        # Create directory if it doesn't exist
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            print(f"Camera {self._id}: Error creating directory {folder_path}: {e}")
            return None
        
        # Generate timestamp prefix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{image_name}.png"
        full_path = os.path.join(folder_path, filename)
        
        # Save the image as PNG
        try:
            # Debug: print image information
            print(f"Camera {self._id}: Image shape: {frame_to_save.shape}")
            print(f"Camera {self._id}: Image dtype: {frame_to_save.dtype}")
            print(f"Camera {self._id}: Image min/max: {frame_to_save.min()}/{frame_to_save.max()}")
            
            # Apply rotation if needed (before format conversion)
            if self.rotate_img:
                frame_to_save = cv2.rotate(frame_to_save, cv2.ROTATE_90_CLOCKWISE)
            
            # Always save as 16-bit PNG to preserve maximum dynamic range
            if frame_to_save.dtype == 'uint16':
                # Already 16-bit, save directly
                print(f"Camera {self._id}: Saving native 16-bit data")
                success = cv2.imwrite(full_path, frame_to_save)
            elif frame_to_save.dtype == 'uint8':
                # Convert 8-bit to 16-bit by scaling up
                frame_16bit = (frame_to_save.astype('uint16') * 257)  # 257 = 65535/255
                print(f"Camera {self._id}: Upscaling 8-bit to 16-bit")
                success = cv2.imwrite(full_path, frame_16bit)
            else:
                # Normalize other formats to 16-bit range
                frame_16bit = cv2.normalize(frame_to_save, None, 0, 65535, cv2.NORM_MINMAX, dtype=cv2.CV_16U)
                print(f"Camera {self._id}: Normalizing to 16-bit")
                success = cv2.imwrite(full_path, frame_16bit)
            
            if success:
                print(f"Camera {self._id}: 16-bit image saved to {full_path}")
                return full_path
            else:
                print(f"Camera {self._id}: Failed to save image to {full_path}")
                return None
                
        except Exception as e:
            print(f"Camera {self._id}: Error saving image: {e}")
            return None



