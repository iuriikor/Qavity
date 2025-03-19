"""
capi.py: This file contains the C API for xeneth.dll.
"""

from sys import platform
import ctypes
import ctypes.util


# pylint: disable=protected-access,broad-exception-raised,global-statement,invalid-name

xenethdll = None
if platform != 'win32':
    raise SystemError("This module currently only works on the Windows platform")



def _load_library():
    global xenethdll
    # select xeneth.dll; 32 bit ot 64 bit version
    _loaded_32 = _loaded_64 = False
    _err_32 = _err_64 = None

    try:
        xenethdll = ctypes.WinDLL(ctypes.util.find_library("xeneth"))
    except OSError as e:
        _err_32 = e
    else:
        _loaded_32 = True
        xenethdll._name = 'xeneth'

    if not _loaded_32:
        try:
            xenethdll = ctypes.WinDLL(ctypes.util.find_library("xeneth64"))
        except OSError as e:
            _err_64 = e
        else:
            _loaded_64 = True
            xenethdll._name = 'xeneth64'


    # inject '_bitness' attribute to xenethdll
    if _loaded_32:
        xenethdll._bitness_32 = True
        xenethdll._bitness_64 = False
    elif _loaded_64:
        xenethdll._bitness_32 = False
        xenethdll._bitness_64 = True
    else:
        msg = """could not load xeneth.dll (32bit) nor xeneth64.dll (64bit)
        Is there a Xeneth installed that matches the bitness of the Python interpreter?
        """
        raise Exception(msg)

    # inject '_path' attribute to xenethdll
    xenethdll._path = ctypes.util.find_library(xenethdll._name)

_load_library()
