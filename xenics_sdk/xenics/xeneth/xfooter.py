"""
xfooters.py
Footer classes
"""

from xenics.xeneth.capi.structs import XPFF_GENERIC

class PFFGeneric():
    """
    Per frame footer combining both the software and hardware footers in one structure.
    """

    def __init__(self, c_struct: XPFF_GENERIC = XPFF_GENERIC()):
        super().__init__()

        self._len = c_struct.len
        self._ver = c_struct.ver
        self._soc = c_struct.soc
        self._tft = c_struct.tft
        self._tfc = c_struct.tfc
        self._fltref = c_struct.fltref
        self._hfl = c_struct.hfl
        self._pid = c_struct.common.pid

        # Assign the corresponding class based on the pid
        if self._pid == 0xF040:
            self._camera_footer = c_struct.common.onca
        elif self._pid == 0xF003:
            self._camera_footer = c_struct.common.gobi
        elif self._pid == 0xF090:
            self._camera_footer = c_struct.common.tigris
        elif self._pid == 0xF086:
            self._camera_footer = c_struct.common.manx
        else:
            self._camera_footer = None

    @property
    def len(self) -> int:
        """
        Structure length
        """
        return self._len

    @property
    def ver(self) -> int:
        """
        Version (0xAA00)
        """
        return self._ver

    @property
    def soc(self) -> int:
        """
        Time of Start Capture
        """
        return self._soc

    @property
    def tft(self) -> int:
        """
        Time of reception
        """
        return self._tft

    @property
    def tfc(self) -> int:
        """
        Frame counter
        """
        return self._tfc

    @property
    def fltref(self) -> int:
        """
        Filter marker, top nibble specifies purpose
        0x1xxxxxxx - Filter generated trigger event (x = filter specific)
        0x2xxxxxxx - Start / end of sub-sequence marker (x = 0 / x = 1)
        """
        return self._fltref

    @property
    def hfl(self) -> int:
        """
        Hardware footer length
        """
        return self._hfl

    @property
    def pid(self) -> int:
        """
        Hardware footer PID
        """
        return self._pid

    @property
    def camera_footer(self):
        """
        Camera hardware footer
        """
        return self._camera_footer
