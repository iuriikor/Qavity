"""
XFrameBuffer class
"""

import math
import numpy as np
from xenics.xeneth.capi.enums import XFrameType
from xenics.xeneth.capi.structs import XPFF_GENERIC
from xenics.xeneth.errors import XenethException
from xenics.xeneth.xfooter import PFFGeneric


class XFrameBuffer(object):
    """
    Class representing an image frame buffer.
    This buffer supports multiple image frame types such as grayscale or color (RGB, RGBA, etc.)
    """
    def __init__(self, width: int, height: int, frame_type: XFrameType, footer_length: int):
        super().__init__()

        self._width = width
        self._height = height
        self._frame_type = frame_type
        self._footer_length = footer_length
        self._np_type = None
        self._bytes_per_pixel = 1
        self._channels = 1

        if frame_type == XFrameType.FT_8_BPP_GRAY:
            self._np_type = np.uint8
            self._bytes_per_pixel = 1
            self._channels = 1
        elif frame_type == XFrameType.FT_16_BPP_GRAY:
            self._np_type = np.uint16
            self._bytes_per_pixel = 2
            self._channels = 1
        elif frame_type in [XFrameType.FT_32_BPP_RGB,
                                 XFrameType.FT_32_BPP_BGR]:
            self._np_type = np.uint8
            self._bytes_per_pixel = 3
            self._channels = 3
        elif frame_type in [XFrameType.FT_32_BPP_GRAY,
                                 XFrameType.FT_32_BPP_RGBA,
                                 XFrameType.FT_32_BPP_BGRA]:
            self._np_type = np.uint8
            self._bytes_per_pixel = 4
            self._channels = 4
        elif frame_type == XFrameType.FT_NATIVE:
            raise XenethException(f"Specific frame type must be specified. Given frame type: {frame_type}")
        else:
            raise XenethException(f"Unsupported frame type: {frame_type}")


        # Calculate the number of extra rows needed to fit the footer
        self._footer_rows =  math.ceil((self._footer_length / self.width) / self._bytes_per_pixel)

        self._size = self._width * self._height * self._bytes_per_pixel

        if self._channels == 1:
            self._data = np.ndarray(shape=(self._height + self._footer_rows, self._width), dtype=self._np_type)
        else:
            self._data = np.ndarray(shape=(self._height + self._footer_rows, self._width, self._channels), dtype=self._np_type)


    @property
    def width(self) -> int:
        """
        The width of the frame buffer.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The height (rows) of the frame buffer (excluding footer).
        """
        return self._height

    @property
    def frame_type(self) -> XFrameType:
        """
        Frame type for which the buffer was created
        """
        return self._frame_type

    @property
    def channels(self) -> int:
        """
        The number of color channels
        """
        return self._channels

    @property
    def bytes_per_pixel(self) -> int:
        """
        The number of bytes per pixel
        """
        return self._bytes_per_pixel

    @property
    def footer_length(self) -> int:
        """
        The footer length in bytes
        """
        return self._footer_length

    @property
    def data(self) -> np.ndarray:
        """
        The image buffer itself INCLUDING footer.
        This is a numpy array of shape (height + footer_rows, width, channels) for multichannel formats (RGBA, BGRA, ...)
        or shape (height + footer_rows, width) for single channel formats (Grayscale), with dtype varying based on frame type
        """
        return self._data

    @property
    def image_data(self) -> np.ndarray:
        """
        The image buffer itself without footer.
        This is a numpy array of shape (height + footer_rows, width, channels) for multichannel formats (RGBA, BGRA, ...)
        or shape (height + footer_rows, width) for single channel formats (Grayscale), with dtype varying based on frame type
        """
        return self._data[0:self._height][0:self._width]

    @property
    def size(self) -> int:
        """
        Returns the size of the frame image buffer in bytes.
        Excludes the footer.
        """
        return self._size

    @property
    def total_size(self) -> int:
        """
        Returns the size of the frame image buffer in bytes.
        Includes the footer, padded to a full row.
        """
        return self._data.nbytes

    def extract_footer(self) -> PFFGeneric:
        """
        Extracts the frame footer from the frame buffer.

        returns: A PFFGeneric instance that represents the extracted frame footer.
        """

        footer = XPFF_GENERIC.from_buffer_copy(self.data, self.size)
        gen = PFFGeneric(footer)
        return gen
    