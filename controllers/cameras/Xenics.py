import time
import cv2
import os
import numpy as np

from datetime import datetime
from xenics.xeneth import *
from xenics.xeneth.errors import XenethAPIException

from .Camera import Camera

from logger_config import get_logger
logger = get_logger(__name__)

class Xenics(Camera):
    def __init__(self, cam_id, framerate=10, exposure_ms=1):
        super().__init__(cam_id)
        self._buffer = None
        # Initialize background subtraction variables
        self.background_image = None
        self.background_path = None
        self.remove_bg = False
        self.roi_x_tl = None
        self.roi_y_tl = None
        self.roi_x_br = None
        self.roi_y_br = None
        try:
            self._camera = XCamera()
            self._camera.open(cam_id)
            logger.info(f"Opened connection to Xenics camera, ID {self._id}")
        except XenethAPIException as e:
            logger.error(f"Xenics camera error: {e.message}")

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            logger.error(f"Exception: {exception_traceback}")
        self.close()
        return True if exception_type is None else False

    def initialize(self, framerate=10, exposure_ms=1):
        self.framerate = framerate
        try:
            self._buffer = self._camera.create_buffer()
            if self._camera.is_initialized:
                self.sensor_width = self._camera.max_width
                self.sensor_height = self._camera.max_height
                self.set_exposure_ms(exposure_ms)
                self._camera.start_capture()
                logger.info(f"Camera {self._id} initialized")
            else:
                logger.error(f"Camera {self._id} initialization failed")
        except XenethAPIException as e:
            logger.error(f"Camera {self._id} initialization error: {e.message}")

    def _apply_background_subtraction(self, frame):
        """
        Apply background subtraction to the frame.
        Handles ROI by cropping the background image to match the current frame size.

        Args:
            frame: Input frame from camera (may be ROI-cropped)

        Returns:
            numpy.ndarray: Frame with background subtracted, values clipped to [0, max]
        """
        try:
            # Get the appropriate background region
            background_region = self._get_background_region_for_frame(frame)

            if background_region is None:
                logger.warning(f"Camera {self._id}: Could not extract background region")
                return frame

            # Ensure frame and background region have the same shape
            if frame.shape != background_region.shape:
                logger.warning(
                    f"Camera {self._id}: Frame shape {frame.shape} != background region shape {background_region.shape}")
                return frame

            # Convert to signed integer to handle negative results
            if frame.dtype == 'uint8':
                frame_signed = frame.astype('int16')
                bg_signed = background_region.astype('int16')
                max_val = 255
            elif frame.dtype == 'uint16':
                frame_signed = frame.astype('int32')
                bg_signed = background_region.astype('int32')
                max_val = 65535
            else:
                # Handle other data types
                frame_signed = frame.astype('float32')
                bg_signed = background_region.astype('float32')
                max_val = frame.max()

            # Subtract background
            subtracted = frame_signed - bg_signed

            # Clip negative values to 0 and maintain maximum value
            clipped = np.clip(subtracted, 0, max_val)

            # Convert back to original data type
            result = clipped.astype(frame.dtype)

            return result

        except Exception as e:
            logger.error(f"Camera {self._id}: Error in background subtraction: {e}")
            return frame  # Return original frame on error

    def _get_background_region_for_frame(self, frame):
        """
        Extract the appropriate region from the background image to match the current frame.
        Handles ROI by cropping the full-sensor background image.

        Args:
            frame: Current camera frame (potentially ROI-cropped)

        Returns:
            numpy.ndarray: Background region matching the frame dimensions
        """
        try:
            # If no ROI is set, frame should match background
            if (self.roi_x_tl is None or self.roi_y_tl is None or
                    self.roi_x_br is None or self.roi_y_br is None):
                # No ROI set, use full background
                return self.background_image

            # ROI is set, crop background to match the ROI region
            # Always use the actual frame dimensions to crop the background
            frame_height, frame_width = frame.shape[:2]

            # Crop background using the ROI coordinates but matching actual frame size
            try:
                # Calculate the end coordinates based on ROI start + frame dimensions
                y_end = self.roi_y_tl + frame_height
                x_end = self.roi_x_tl + frame_width

                # Ensure we don't go beyond background image boundaries
                y_end = min(y_end, self.background_image.shape[0])
                x_end = min(x_end, self.background_image.shape[1])

                # Crop background image to match frame
                background_roi = self.background_image[self.roi_y_tl:y_end,
                                 self.roi_x_tl:x_end]

                # Final size check - if still doesn't match, crop to exact frame size
                if background_roi.shape[:2] != frame.shape[:2]:
                    background_roi = background_roi[:frame_height, :frame_width]

                return background_roi

            except Exception as slice_error:
                logger.error(f"Camera {self._id}: Error with ROI slicing: {slice_error}")

                # Ultimate fallback: crop from top-left of background to match frame size
                if (frame_height <= self.background_image.shape[0] and
                        frame_width <= self.background_image.shape[1]):
                    background_roi = self.background_image[:frame_height, :frame_width]
                    return background_roi
                else:
                    logger.error(f"Camera {self._id}: Cannot crop background - frame larger than background")
                    return self.background_image

        except Exception as e:
            logger.error(f"Camera {self._id}: Error extracting background region: {e}")
            return None


    def get_frame(self):
        logger.debug('XENICS: getting frame')
        if self._buffer is not None:
            logger.debug('XENICS: buffer initialized correctly')
            if self._camera.get_frame(self._buffer, flags=XGetFrameFlags.XGF_Blocking):
                logger.debug('XENICS: image acquired and not None')
                img = cv2.normalize(self._buffer.image_data, None, 0, 65535, cv2.NORM_MINMAX, dtype=cv2.CV_16U)
                # Apply background subtraction if enabled
                if self.remove_bg and self.background_image is not None:
                    processed_frame = self._apply_background_subtraction(img)
                else:
                    processed_frame = img
                
                # Convert 16-bit to 8-bit for streaming display
                # Use the full dynamic range of the current frame
                display_frame = cv2.normalize(processed_frame, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                return display_frame
            else:
                return None
        else:
            raise Exception("Xenics camera buffer not initialized")

    def close(self):
        if self._camera.is_capturing:
            try:
                logger.info(f"Camera {self._id} stopping capture")
                self._camera.stop_capture()
                logger.info(f"Camera {self._id} closing")
                self._camera.close()
            except XenethAPIException as e:
                logger.error(f"Camera {self._id} close error: {e.message}")

    def __del__(self):
        self.close()
        logger.info(f"Camera {self._id} closed")

    def set_exposure_ms(self, exposure_ms):
        try:
            self._camera.set_property_value('ExposureTime', exposure_ms * 1e03)
            self.exposure_ms = exposure_ms
        except XenethAPIException as e:
            logger.error(f"Camera {self._id} exposure setting error: {e.message}")

    def get_exposure_ms(self):
        try:
            exposure_us = self._camera.get_property_value('ExposureTime')
            return exposure_us/1000.0
        except XenethAPIException as e:
            logger.error(f"Camera {self._id} exposure reading error: {e.message}")
            return None

    def stop_stream(self):
        """Stop streaming but keep the camera running"""
        logger.info(f"Camera {self._id} stopping stream...")
        self.streamOn = False
        logger.debug(f"Camera {self._id} stream flag set to: {self.streamOn}")

    def start_stream(self):
        self.streamOn = True

    def set_ROI(self, upper_left_x_pixels, upper_left_y_pixels,
                lower_right_x_pixels, lower_right_y_pixels):
        """
        Sets ROI of the camera using 2 pairs or X-Y pixel coordintates, top left and bottom right.
        Note: camera coordinate systems usually start from the top-left corner
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
        # Convert to Xenics format of Window of interest, which is offset and width or height
        offset_x = self.roi_x_tl
        offset_y = self.roi_y_tl
        width_x = self.roi_x_br - self.roi_x_tl
        height_y = self.roi_y_br - self.roi_y_tl
        try:
            self._camera.set_property_value("OffsetX", offset_x)
            self._camera.set_property_value("Width", width_x)
            self._camera.set_property_value("OffsetY", offset_y)
            self._camera.set_property_value("Height", height_y)
            # Arm again
            self._buffer = self._camera.create_buffer()
        except Exception as e:
            logger.error(f"Camera {self._id}: Error setting ROI: {e}")

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
        if self._buffer is not None:
            frame_to_save = cv2.normalize(self._buffer.image_data, None, 0, 65535, cv2.NORM_MINMAX, dtype=cv2.CV_16U)
            logger.debug(f"Camera {self._id}: Using existing frame for save")
        else:
            # Try to get a new frame
            logger.debug(f"Camera {self._id}: Getting new frame for save")
            self._camera.get_frame(self._buffer, flags=XGetFrameFlags.XGF_Blocking)
            frame_to_save = cv2.normalize(self._buffer.image_data, None, 0, 65535, cv2.NORM_MINMAX, dtype=cv2.CV_16U)

        # Check if we have a valid frame
        if frame_to_save is None:
            logger.warning(f"Camera {self._id}: No frame available to save")
            return None

        # Create directory if it doesn't exist
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            logger.error(f"Camera {self._id}: Error creating directory {folder_path}: {e}")
            return None

        # Generate timestamp prefix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{image_name}.png"
        full_path = os.path.join(folder_path, filename)

        # Save the image as PNG
        try:
            # Apply rotation if needed (before format conversion)
            if self.rotate_img:
                frame_to_save = cv2.rotate(frame_to_save, cv2.ROTATE_90_CLOCKWISE)

            # Always save as 16-bit PNG to preserve maximum dynamic range
            if frame_to_save.dtype == 'uint16':
                # Already 16-bit, save directly
                success = cv2.imwrite(full_path, frame_to_save)
            elif frame_to_save.dtype == 'uint8':
                # Convert 8-bit to 16-bit by scaling up
                frame_16bit = (frame_to_save.astype('uint16') * 257)  # 257 = 65535/255
                success = cv2.imwrite(full_path, frame_16bit)
            else:
                # Normalize other formats to 16-bit range
                frame_16bit = cv2.normalize(frame_to_save, None, 0, 65535, cv2.NORM_MINMAX, dtype=cv2.CV_16U)
                success = cv2.imwrite(full_path, frame_16bit)

            if success:
                logger.info(f"Camera {self._id}: Image saved to {full_path}")
                return full_path
            else:
                logger.error(f"Camera {self._id}: Failed to save image to {full_path}")
                return None

        except Exception as e:
            logger.error(f"Camera {self._id}: Error saving image: {e}")
            return None

    def set_background_path(self, background_path):
        """
        Set the path to the background image file and load it.

        Args:
            background_path (str): Full path to the background image file

        Returns:
            bool: True if background loaded successfully, False otherwise
        """
        if not background_path or not os.path.exists(background_path):
            logger.warning(f"Camera {self._id}: Background path does not exist: {background_path}")
            return False

        try:
            # Load the background image
            background_img = cv2.imread(background_path, cv2.IMREAD_UNCHANGED)
            if background_img is None:
                logger.error(f"Camera {self._id}: Failed to load background image: {background_path}")
                return False

            # Store the background image and path
            self.background_path = background_path
            self.background_image = background_img
            logger.info(f"Camera {self._id}: Background image loaded from {background_path}")
            logger.debug(f"Camera {self._id}: Background shape: {background_img.shape}, dtype: {background_img.dtype}")
            return True

        except Exception as e:
            logger.error(f"Camera {self._id}: Error loading background image: {e}")
            return False

    def set_background_subtraction(self, enable):
        """
        Enable or disable background subtraction.

        Args:
            enable (bool): True to enable background subtraction, False to disable
        """
        self.remove_bg = enable
        status = "enabled" if enable else "disabled"
        logger.info(f"Camera {self._id}: Background subtraction {status}")

    def get_background_path(self):
        """Get the current background image path."""
        return self.background_path

    def is_background_subtraction_enabled(self):
        """Check if background subtraction is enabled."""
        return self.remove_bg
