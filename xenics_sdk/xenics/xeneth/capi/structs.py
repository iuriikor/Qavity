"""
structs.py

SDK Structures
"""

import ctypes
from xenics.xeneth.capi.enums import XDeviceStates


# Name conventions are from the C API. disable pylint check
# pylint: disable=invalid-name
# pylint: disable=protected-access

class XDeviceInformation(ctypes.Structure):
    """
    Device information structure

    This structure holds all details needed to set up a connection to a discovered device.
    Use this structure in combination with the XCD_EnumerateDevices() function.
    In case a direct connection using a protocol-specific URL was established, it is also
    possible to catch the XDeviceInformation structure in the XStatus callback.
    """

    _pack_ = 1
    _fields_ = [
        ("_size", ctypes.c_int),
        ("_name", ctypes.c_char * 64),
        ("_transport", ctypes.c_char * 64),
        ("_url", ctypes.c_char * 256),
        ("_address", ctypes.c_char * 64),
        ("_serial", ctypes.c_uint),
        ("_pid", ctypes.c_uint),
        ("_state", ctypes.c_int),
    ]

    # size property not added as it is irrelevant for the python implementation

    @property
    def name(self) -> str:
        """String containing the device's model name"""
        return self._name.decode()

    @property
    def transport(self) -> str:
        """Serial | CoaXPress | GigEVision | Network | CameraLink | CameraLink GenCP"""
        return self._transport.decode()

    @property
    def url(self) -> str:
        """URL identifying the camera internally. e.g. cam://0..n"""
        return self._url.decode()

    @property
    def address(self) -> str:
        """The address where the device resides, the format is protocol specific. e.g. 192.168.2.2 | COM0..n | CL0..n::( NationalInstruments | Euresys | Imperx ... )"""
        return self._address.decode()

    @property
    def serial(self) -> int:
        """Serial number reported by the camera. e.g. 0x12345678"""
        return self._serial

    @property
    def pid(self) -> int:
        """Product id reported by the camera. e.g. 0x0000F020"""
        return self._pid

    @property
    def state(self) -> XDeviceStates:
        """Camera status to determine if the camera is in use at that time."""
        return XDeviceStates(self._state)


class XPFF(ctypes.Structure):
    """
    Per frame software footer.

    Use XCamera::GetFrameFooterLength() to determine the exact size in bytes of both soft and hardware footers.
    For more detailed information about footers refer to the XFooters.h-header. To learn how to retrieve
    the per frame footer make sure to check XCamera::GetFrame(FrameType, unsigned long, void *, unsigned int) and the #XGF_FetchPFF-flag.
    """

    _pack_ = 1
    _fields_ = [
        ("_len", ctypes.c_ushort),
        ("_ver", ctypes.c_ushort),
        ("_soc", ctypes.c_longlong),
        ("_tft", ctypes.c_longlong),
        ("_tfc", ctypes.c_uint),
        ("_fltref", ctypes.c_uint),
        ("_hfl", ctypes.c_uint),
    ]

    @property
    def len(self) -> int:
        """Structure length"""
        return self._len

    @property
    def ver(self) -> int:
        """Fixed to 0xAA00"""
        return self._ver

    @property
    def soc(self) -> int:
        """Time of Start Capture (us since start of epoch)"""
        return self._soc

    @property
    def tft(self) -> int:
        """Time of reception (us since start of epoch)"""
        return self._tft

    @property
    def tfc(self) -> int:
        """Frame counter"""
        return self._tfc

    @property
    def fltref(self) -> int:
        """Reference for attaching messages/frame (described in #XFooters.h)"""
        return self._fltref

    @property
    def hfl(self) -> int:
        """Hardware footer length"""
        return self._hfl



class _XPFF_F040_StatusBits(ctypes.Structure):
    """
    Bits for the XPFF_F040 status field
    """
    _pack_ = 1
    _fields_ = [
        ("_trig_ext", ctypes.c_ushort, 1),
        ("_trig_cl", ctypes.c_ushort, 1),
        ("_trig_soft", ctypes.c_ushort, 1),
        ("_reserved", ctypes.c_ushort, 5),
        ("_linecam_fixedSH", ctypes.c_ushort, 1),
        ("_linecam_SHBfirst", ctypes.c_ushort, 1),
        ("_reserved2", ctypes.c_ushort, 3),
        ("_filterwheel", ctypes.c_ushort, 3),
    ]

class _XPFF_F040_Status(ctypes.Union):
    """
    XPFF_F040 status structure
    """
    _pack_ = 1
    _fields_ = [
        ("_statusbits", _XPFF_F040_StatusBits),
        ("_field", ctypes.c_ushort),
    ]

    @property
    def field(self) -> int:
        """Status field"""
        return self._field

    @property
    def trig_ext(self) -> bool:
        """External trigger state"""
        return bool(self._statusbits._trig_ext)

    @property
    def trig_cl(self) -> bool:
        """Camera link trigger pin state"""
        return bool(self._statusbits._trig_cl)

    @property
    def trig_soft(self) -> bool:
        """Software trigger state"""
        return bool(self._statusbits._trig_soft)

    @property
    def reserved(self) -> int:
        """RFU"""
        return self._statusbits._reserved

    @property
    def linecam_fixedSH(self) -> bool:
        """Line camera: uses single readout"""
        return bool(self._statusbits._linecam_fixedSH)

    @property
    def linecam_SHBfirst(self) -> bool:
        """Line camera: order of the lines"""
        return bool(self._statusbits._linecam_SHBfirst)

    @property
    def reserved2(self) -> int:
        """RFU"""
        return self._statusbits._reserved2

    @property
    def filterwheel(self) -> int:
        """Current filter wheel position"""
        return self._statusbits._filterwheel

class XPFF_F040(ctypes.Structure):
    """
    Hardware footer structure for ONCA class cameras (class PID = 0xf040)
    """
    _pack_ = 1

    _fields_ = [
        ("_status", _XPFF_F040_Status),
        ("_tint", ctypes.c_uint),
        ("_timelo", ctypes.c_uint),
        ("_timehi", ctypes.c_uint),
        ("_temp_die", ctypes.c_ushort),
        ("_temp_case", ctypes.c_ushort),
    ]

    @property
    def status(self) -> _XPFF_F040_Status:
        """Status"""
        return self._status

    @property
    def tint(self) -> int:
        """Active exposure time in truncated us"""
        return self._tint

    @property
    def timelo(self) -> int:
        """Timestamp lo"""
        return self._timelo

    @property
    def timehi(self) -> int:
        """Timestamp hi (64-bit since the start of the Unix epoch)"""
        return self._timehi

    @property
    def temp_die(self) -> int:
        """Die temperature in degrees Kelvin"""
        return self._temp_die

    @property
    def temp_case(self) -> int:
        """Case temperature in degrees Kelvin"""
        return self._temp_case



class _XPFF_F003_StatusBits(ctypes.Structure):
    """
    Status bits for the XPFF_F003 structure
    """
    _pack_ = 1
    _fields_ = [
        ("_trig_ext", ctypes.c_ushort, 1),
        ("_reserved", ctypes.c_ushort, 15),
    ]

class _XPFF_F003_Status(ctypes.Union):
    """
    Status for the XPFF_F003 structure
    """
    _pack_ = 1
    _fields_ = [
        ("_statusbits", _XPFF_F003_StatusBits),
        ("_field", ctypes.c_ushort),
    ]

    @property
    def field(self) -> int:
        """Status field"""
        return self._field

    @property
    def trig_ext(self) -> bool:
        """External trigger state"""
        return bool(self._statusbits._trig_ext)

    @property
    def reserved(self) -> int:
        """Reserved"""
        return self._statusbits._reserved

class XPFF_F003(ctypes.Structure):
    """
    Hardware footer structure for GOBI class cameras (class PID = 0xf003)
    """
    _pack_ = 1
    _fields_ = [
        ("_status", _XPFF_F003_Status),
        ("_tint", ctypes.c_uint),
        ("_timelo", ctypes.c_uint),
        ("_timehi", ctypes.c_uint),
        ("_temp_die", ctypes.c_ushort),
        ("_reserved1", ctypes.c_ushort),
        ("_tag", ctypes.c_ushort),
        ("_image_offset", ctypes.c_uint),
        ("_image_gain", ctypes.c_ushort),
        ("_frame_cnt", ctypes.c_ushort),
        ("_reserved2", ctypes.c_ushort),
    ]

    @property
    def status(self) -> _XPFF_F003_Status:
        """Status"""
        return self._status


    @property
    def tint(self) -> int:
        """Integration time in microseconds"""
        return self._tint

    @property
    def timelo(self) -> int:
        """Time stamp low"""
        return self._timelo

    @property
    def timehi(self) -> int:
        """Time stamp hi (64-bit integer since the start of the Unix epoch)"""
        return self._timehi

    @property
    def temp_die(self) -> int:
        """Sensor temperature (Die temp) in centiKelvin"""
        return self._temp_die

    @property
    def reserved1(self) -> int:
        """Reserved"""
        return self._reserved1

    @property
    def tag(self) -> int:
        """Tag"""
        return self._tag

    @property
    def image_offset(self) -> int:
        """Global offset applied to all pixels in the frame (signed 32-bit number)"""
        return self._image_offset

    @property
    def image_gain(self) -> int:
        """Global gain applied to the pixels in the frame (8.8 fixed point number)"""
        return self._image_gain

    @property
    def frame_cnt(self) -> int:
        """Frame counter"""
        return self._frame_cnt

    @property
    def reserved2(self) -> int:
        """Reserved"""
        return self._reserved2



class XPFF_F090(ctypes.Structure):
    """
    Hardware footer structure for XCO class cameras (class PID = 0xf090)
    """
    _pack_ = 1

    _fields_ = [
        ("_status", ctypes.c_ushort),
        ("_timelo", ctypes.c_uint),
        ("_timehi", ctypes.c_uint),
        ("_counter", ctypes.c_uint),
        ("_sample_counter", ctypes.c_uint),
        ("_offset_x", ctypes.c_ushort),
        ("_offset_y", ctypes.c_ushort),
        ("_reserved2", ctypes.c_uint),
        ("_reserved3", ctypes.c_uint),
        ("_reserved4", ctypes.c_uint),
        ("_reserved5", ctypes.c_uint),
        ("_reserved6", ctypes.c_uint),
        ("_reserved7", ctypes.c_uint),
        ("_reserved8", ctypes.c_uint),
        ("_reserved9", ctypes.c_uint),
        ("_reserved10", ctypes.c_uint),
        ("_reserved11", ctypes.c_uint),
    ]

    @property
    def status(self) -> int:
        """Status"""
        return self._status

    @property
    def timelo(self) -> int:
        """Time stamp low"""
        return self._timelo

    @property
    def timehi(self) -> int:
        """Time stamp hi (64-bit integer since the start of the Unix epoch)"""
        return self._timehi

    @property
    def counter(self) -> int:
        """Counter"""
        return self._counter

    @property
    def sample_counter(self) -> int:
        """Sample counter"""
        return self._sample_counter

    @property
    def offset_x(self) -> int:
        """X offset"""
        return self._offset_x

    @property
    def offset_y(self) -> int:
        """Y offset"""
        return self._offset_y

    @property
    def reserved2(self) -> int:
        """Reserved"""
        return self._reserved2

    @property
    def reserved3(self) -> int:
        """Reserved"""
        return self._reserved3

    @property
    def reserved4(self) -> int:
        """Reserved"""
        return self._reserved4

    @property
    def reserved5(self) -> int:
        """Reserved"""
        return self._reserved5

    @property
    def reserved6(self) -> int:
        """Reserved"""
        return self._reserved6

    @property
    def reserved7(self) -> int:
        """Reserved"""
        return self._reserved7

    @property
    def reserved8(self) -> int:
        """Reserved"""
        return self._reserved8

    @property
    def reserved9(self) -> int:
        """Reserved"""
        return self._reserved9

    @property
    def reserved10(self) -> int:
        """Reserved"""
        return self._reserved10

    @property
    def reserved11(self) -> int:
        """Reserved"""
        return self._reserved11


class _XPFF_F086_StatusBits(ctypes.Structure):
    """
    Status bits for the XPFF_F086 structure
    """
    _pack_ = 1
    _fields_ = [
        ("_first_line_index", ctypes.c_ushort, 1),
        ("_reserved", ctypes.c_ushort, 15),
    ]

class _XPFF_F086_Status(ctypes.Union):
    """
    Status for the XPFF_F086 structure
    """
    _pack_ = 1
    _fields_ = [
        ("_statusbits", _XPFF_F086_StatusBits),
        ("_field", ctypes.c_ushort),
    ]

    @property
    def field(self) -> int:
        """Status field"""
        return self._field


    @property
    def first_line_index(self) -> bool:
        """Index of the first line in the image"""
        return bool(self._statusbits._first_line_index)

    @property
    def reserved(self) -> int:
        """Reserved"""
        return self._statusbits._reserved

class XPFF_F086(ctypes.Structure):
    """
    Hardware footer structure for Manx class cameras (class PID = 0xf086)
    """
    _pack_ = 1

    _fields_ = [
        ("_status", _XPFF_F086_Status),
        ("_timelo", ctypes.c_uint),                   # Time stamp low
        ("_timehi", ctypes.c_uint),                   # Time stamp hi (64-bit integer since the start of the Unix epoch)
        ("_frame_counter", ctypes.c_uint),
        ("_reserved0", ctypes.c_uint),
        ("_reserved1", ctypes.c_uint),
        ("_reserved2", ctypes.c_uint),
        ("_reserved3", ctypes.c_uint),
        ("_reserved4", ctypes.c_uint),
        ("_reserved5", ctypes.c_uint),
        ("_reserved6", ctypes.c_uint),
        ("_reserved7", ctypes.c_uint),
        ("_reserved8", ctypes.c_uint),
        ("_reserved9", ctypes.c_uint),
        ("_reserved10", ctypes.c_uint),
        ("_reserved11", ctypes.c_uint),
    ]

    @property
    def status(self) -> _XPFF_F086_Status:
        """Status bits"""
        return self._status

    @property
    def timelo(self) -> int:
        """Time stamp low"""
        return self._timelo

    @property
    def timehi(self) -> int:
        """Time stamp hi (64-bit integer since the start of the Unix epoch)"""
        return self._timehi

    @property
    def frame_counter(self) -> int:
        """Frame counter"""
        return self._frame_counter

    @property
    def reserved0(self) -> int:
        """Reserved"""
        return self._reserved0

    @property
    def reserved1(self) -> int:
        """Reserved"""
        return self._reserved1

    @property
    def reserved2(self) -> int:
        """Reserved"""
        return self._reserved2

    @property
    def reserved3(self) -> int:
        """Reserved"""
        return self._reserved3

    @property
    def reserved4(self) -> int:
        """Reserved"""
        return self._reserved4

    @property
    def reserved5(self) -> int:
        """Reserved"""
        return self._reserved5

    @property
    def reserved6(self) -> int:
        """Reserved"""
        return self._reserved6

    @property
    def reserved7(self) -> int:
        """Reserved"""
        return self._reserved7

    @property
    def reserved8(self) -> int:
        """Reserved"""
        return self._reserved8

    @property
    def reserved9(self) -> int:
        """Reserved"""
        return self._reserved9

    @property
    def reserved10(self) -> int:
        """Reserved"""
        return self._reserved10

    @property
    def reserved11(self) -> int:
        """Reserved"""
        return self._reserved11



class _XPFF_GENERIC_Common(ctypes.Union):
    """
    Common for the XPFF_GENERIC structure
    """
    _pack_ = 1
    _fields_ = [
        ("_pid", ctypes.c_ushort),          # Footer class identifier
        ("_onca", XPFF_F040),               # PID == 0xF040
        ("_gobi", XPFF_F003),               # PID == 0xF020, 0xF021, 0xF031
        ("_tigris", XPFF_F090),             # PID == 0xF090
        ("_manx", XPFF_F086),               # PID == 0xF086
    ]

    @property
    def pid(self) -> int:
        """Footer class identifier"""
        return self._pid

    @property
    def onca(self) -> XPFF_F040:
        """XPFF_F040 (PID == 0xF040)"""
        return self._onca

    @property
    def gobi(self) -> XPFF_F003:
        """XPFF_F003 (PID == 0xF020, 0xF021, 0xF031)"""
        return self._gobi

    @property
    def tigris(self) -> XPFF_F090:
        """XPFF_F090 (PID == 0xF090)"""
        return self._tigris

    @property
    def manx(self) -> XPFF_F086:
        """XPFF_F086 (PID == 0xF086)"""
        return self._manx

class XPFF_GENERIC(ctypes.Structure):
    """
    Per frame footer combining both the software and hardware footers in one structure.
    """
    _pack_ = 1

    _fields_ = [
        ("_len", ctypes.c_ushort),
        ("_ver", ctypes.c_ushort),
        ("_soc", ctypes.c_longlong),
        ("_tft", ctypes.c_longlong),
        ("_tfc", ctypes.c_uint),
        ("_fltref", ctypes.c_uint),
        ("_hfl", ctypes.c_uint),
        ("_common", _XPFF_GENERIC_Common),
    ]

    @property
    def len(self) -> int:
        """Structure length"""
        return self._len

    @property
    def ver(self) -> int:
        """Version (0xAA00)"""
        return self._ver

    @property
    def soc(self) -> int:
        """Time of Start Capture"""
        return self._soc

    @property
    def tft(self) -> int:
        """Time of reception"""
        return self._tft

    @property
    def tfc(self) -> int:
        """Frame counter"""
        return self._tfc

    @property
    def fltref(self) -> int:
        """Filter marker"""
        return self._fltref

    @property
    def hfl(self) -> int:
        """Hardware footer length"""
        return self._hfl

    @property
    def common(self) -> _XPFF_GENERIC_Common:
        """Unified hardware footers"""
        return self._common
    