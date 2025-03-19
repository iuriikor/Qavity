"""
errors.py

XenEth error codes
"""

from enum import IntEnum, unique


@unique
class XErrorCodes(IntEnum):
    """
    Xeneth error codes.
    """
    I_OK                = 0         # Success.
    I_DIRTY             = 1         # Internal.
    E_BUG               = 10000     # Generic.
    E_NOINIT            = 10001     # Camera was not successfully initialized.
    E_LOGICLOADFAILED   = 10002     # Invalid logic file.
    E_INTERFACE_ERROR   = 10003     # Command interface failure.
    E_OUT_OF_RANGE      = 10004     # Provided value is incapable of being produced by the hardware.
    E_NOT_SUPPORTED     = 10005     # Functionality not supported by this camera.
    E_NOT_FOUND         = 10006     # File/Data not found.
    E_FILTER_DONE       = 10007     # Filter has finished processing, and will be removed.
    E_NO_FRAME          = 10008     # A frame was requested by calling GetFrame, but none was available.
    E_SAVE_ERROR        = 10009     # Couldn't save to file.
    E_MISMATCHED        = 10010     # Buffer size mismatch.
    E_BUSY              = 10011     # The API can not read a temperature because the camera is busy.
    E_INVALID_HANDLE    = 10012     # An unknown handle was passed to the C API.
    E_TIMEOUT           = 10013     # Operation timed out.
    E_FRAMEGRABBER      = 10014     # Frame grabber error.
    E_NO_CONVERSION     = 10015     # GetFrame could not convert the image data to the requested format.
    E_FILTER_SKIP_FRAME = 10016     # Filter indicates the frame should be skipped.
    E_WRONG_VERSION     = 10017     # Version mismatch.
    E_PACKET_ERROR      = 10018     # The requested frame cannot be provided because at least one packet has been lost.
    E_WRONG_FORMAT      = 10019     # The emissivity map you tried to set should be a 16 bit greyscale PNG.
    E_WRONG_SIZE        = 10020     # The emissivity map you tried to set has the wrong dimensions (width, height).
    E_CAPSTOP           = 10021     # Internal
    E_OUT_OF_MEMORY     = 10022     # An allocation failed because the system ran out of memory.
    E_RFU               = 10023     # No explanation ?
    