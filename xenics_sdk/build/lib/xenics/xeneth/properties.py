"""
properties.py

Dynamic property access for XCamera
"""

from abc import ABC, abstractmethod
import ctypes
from pathlib import Path
from xenics.xeneth.capi.errors import XErrorCodes
from xenics.xeneth.capi.functions import (
    XC_GetPropertyBlob, XC_GetPropertyRangeE, XC_GetPropertyRangeF,
    XC_GetPropertyUnit, XC_GetPropertyValue,
    XC_GetPropertyValueE, XC_GetPropertyValueF,
    XC_GetPropertyValueL, XC_SetPropertyBlob,
    XC_SetPropertyValue, XC_SetPropertyValueE,
    XC_SetPropertyValueF, XC_SetPropertyValueL
    )

from xenics.xeneth.capi.util import (
    _create_property_enum_value_buffer,
    _create_property_string_value_buffer)

from .errors import PropertyAccess, XCameraAccessException, XCameraInvalidPropertyException, XCameraInvalidValueException, XenethAPIException
from .util import _log as logger, handle_c_call

class Properties():
    """
    An object of this class will hold all properties in its __dict__
    Note that directly using 'object' is not possible; it does not have a __dict__ !!!
    """
    def __getattr__(self, key):
        """Catch any not defined Property """
        raise XCameraInvalidPropertyException(key)

    def __iter__(self):
        """
        Iterate over all properties
        """
        for each in self.__dict__.values():
            yield each

    def __getitem__(self, name):
        """
        Gets a property by name
        """

        # handle case of names ending with '(0)'
        if name.endswith('(0)'):
            name = name[:-3]

        return self.__dict__[name]

    @property
    def propnames(self):
        """
        Returns a list of all property names
        """
        return list(self.__dict__.keys())



class PropertyIface(ABC):
    """ 
    Abstract Base Class for camera properties
    implements access control
    No caching !
    Subclasses must implement _get() and _set()
    """

    def __init__(self, handle, name, proptype, category):
        """
        :param handle:
        :param name: property name
        :param prop_type: property type     eg:
        :param category: property category eg: b'Beginner/Camera/Status/Integration time'
        """
        self.handle = handle
        self.name = name
        self.proptype = proptype
        self.category = category
        # TODO: what is the meaning of readable?
        #   e.g. Number type isn't marked as readable...
        self.readable = (proptype & 0x100) == 0x100
        self.writable = (proptype & 0x200) == 0x200
        self.readonce = (proptype & 0x1000) == 0x1000

    def get(self):
        """
        Reads this property from the camera (we never cache any values)

        :return: property value
        """
        return self._get()

    def set(self, value):
        """
        Writes the given value to this camera property

        :param value: value to write
        """
        if self.writable:
            self._set(value)
        else:
            raise XCameraAccessException(self.name, PropertyAccess.WRITE)

    def _get_property_value_s(self):
        buf = _create_property_string_value_buffer()
        handle_c_call(lambda: XC_GetPropertyValue(self.handle,
                                                  self.name.encode(),
                                                  buf,
                                                  len(buf)))
        return buf.value.decode()

    def _get_property_value_f(self):
        val = ctypes.c_double()
        handle_c_call(lambda: XC_GetPropertyValueF(self.handle,
                                                    self.name.encode(),
                                                    ctypes.byref(val)))
        return val.value

    def _get_property_value_l(self):
        val = ctypes.c_long()
        handle_c_call(lambda: XC_GetPropertyValueL(self.handle,
                                                    self.name.encode(),
                                                    ctypes.byref(val)))
        return val.value

    def _get_property_value_e(self):
        buf = _create_property_enum_value_buffer()
        handle_c_call(lambda: XC_GetPropertyValueE(self.handle,
                                                    self.name.encode(),
                                                    buf,
                                                    len(buf)))
        return buf.value.decode()

    def _get_property_blob(self, size):

        # TODO: Check what to do here.
        # Current use case had a length of 0
        # Calling XC_GetPropertyBlob (with a size of 0) returns error 10003
        # I'm not sure yet if this is the case with 0 only.
        if size == 0:
            return b''

        blob = ctypes.create_string_buffer(size)
        handle_c_call(lambda: XC_GetPropertyBlob(self.handle,
                                                  self.name.encode(),
                                                  blob,
                                                  size))
        return blob.value.decode()

    def _set_property_value_s(self, value):
        handle_c_call(lambda: XC_SetPropertyValue(self.handle,
                                                    self.name.encode(),
                                                    value.encode(),
                                                    "".encode()))

    def _set_property_value_f(self, value):
        val = ctypes.c_double(value)
        handle_c_call(lambda: XC_SetPropertyValueF(self.handle,
                                                    self.name.encode(),
                                                    val,
                                                    "".encode()))

    def _set_property_value_l(self, value):
        val = ctypes.c_long(value)
        handle_c_call(lambda: XC_SetPropertyValueL(self.handle,
                                                    self.name.encode(),
                                                    val,
                                                    "".encode()))

    def _set_property_value_e(self, value):
        handle_c_call(lambda: XC_SetPropertyValueE(self.handle,
                                                    self.name.encode(),
                                                    value.encode()))

    def _set_property_blob(self, value):
        handle_c_call(lambda: XC_SetPropertyBlob(self.handle,
                                                    self.name.encode(),
                                                    value,
                                                    len(value)))

    @abstractmethod
    def _get(self):
        """
        Actual implementation for type specific properties.
        Must be overwritten by subclasses
        """
        raise XCameraAccessException(self.name, PropertyAccess.READ)

    @abstractmethod
    def _set(self, value):
        """
        Actual implementation for type specific properties.
        Must be overwritten by subclasses
        """
        raise XCameraAccessException(self.name, PropertyAccess.WRITE)

class NumProp(PropertyIface):
    """
    Numeric camera property
    All values are read as double floating point data
    """

    def _get(self):
        """
        Read the numeric property from the camera
        """
        return self._get_property_value_f()

    def _set(self, value):
        """Write the numeric property to the camera"""
        self._set_property_value_f(value)

    def get_min_max(self):
        """
        Gets the minimum and maximum values of this property

        :return: (min, max)
        """
        min_value = ctypes.c_double()
        max_value = ctypes.c_double()
        handle_c_call(lambda: XC_GetPropertyRangeF(self.handle,
                                                    self.name.encode(),
                                                    ctypes.byref(min_value),
                                                    ctypes.byref(max_value)))
        
        return min_value.value, max_value.value

    def get_unit(self):
        """
        Gets the unit of this property
        """
        unit_value = _create_property_string_value_buffer()
        handle_c_call(lambda: XC_GetPropertyUnit(self.handle,
                                                self.name.encode(),
                                                unit_value,
                                                len(unit_value)))

        return unit_value.value.decode()

class ActionProp(PropertyIface):
    """Action property
    """
    def execute(self):
        """execute the command"""
        handle_c_call(lambda:  XC_SetPropertyValueL(self.handle, self.name.encode(), 1, b''))


    def _get(self):
        raise XCameraAccessException(self.name, PropertyAccess.READ)

    def _set(self, value):
        self._set_property_value_l(value)


class StringProp(PropertyIface):
    """String property

    Currently limited in size!
    """

    def _get(self):
        """Read the string property"""
        return self._get_property_value_s()

    def _set(self, value):
        """Write the string property"""
        self._set_property_value_s(value)

class EnumProp(PropertyIface):
    """Enumeration property"""

    def __init__(self, handle, name, proptype, category):
        """Initialise the enum property.
        This will also read the possible values for the enum and provide this in the range member.
        """
        super().__init__(handle, name, proptype, category)

        # First try to get the values using a buffer of 512, which should fit most of the time.
        # If the buffer is too small, we get return value E_MISMATCHED
        # As long as we get E_MISMATCHED, try doubling the buffer size.
        propname = self.name.encode()
        bufsize = 512
        buf = ctypes.create_string_buffer(bufsize)
        err = XC_GetPropertyRangeE(self.handle, propname, buf, bufsize)

        while err == XErrorCodes.E_MISMATCHED:
            bufsize *= 2
            buf = ctypes.create_string_buffer(bufsize)
            err = XC_GetPropertyRangeE(self.handle, propname, buf, bufsize)


        # If we get here, the buffer is large enough

        # check for other errors
        if err != XErrorCodes.I_OK:
            raise XenethAPIException(err)


        enum_list = buf.value.decode().split(",")
        self.range = []
        self.range_ui = []
        for i in enum_list:
            self.range.append(i.split("=")[0])
            self.range_ui.append(i.split("=")[1])


    def _get(self):
        """Read the numeric property from the camera"""
        return self._get_property_value_e()

    def _set(self, value):
        """Write the numeric property to the camera"""
        if not (value in self.range):
            raise XCameraInvalidValueException(self.name, value)

        self._set_property_value_e(value)

    def get_range(self):
        """"
        Returns the list of entries.
        :returns:
            - list of programming names
            - List of ui names
        """
        return self.range, self.range_ui


class BoolProp(PropertyIface):
    """
    Boolean property
    """
    def _get(self):
        """Read the boolean property from the camera"""

        return self._get_property_value_l() != 0

    def _set(self, value):
        """Write the boolean property to the camera"""
        self._set_property_value_l(int(value))

class BlobProp(PropertyIface):
    """ Blob property
    """

    @property
    def size(self) -> int:
        """
        Size in bytes of the value.
        """
        return self._get_property_value_l()

    def _set(self, value):
        """
        Write the blob property to the camera.
        """

        if isinstance(value, str) and Path(value).is_file():
            # Set value as string. The SDK will handle the file
            self._set_property_value_s(value)
        elif isinstance(value, bytes):
            # Set value as bytes.
            self._set_property_blob(value)
        else:
            raise XCameraInvalidValueException(self.name, value)

    def _get(self):
        return self._get_property_blob(self.size)
