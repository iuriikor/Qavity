"""
errors.py: Contains exception types Xeneth API.
"""

import ctypes
from enum import IntEnum
from .capi.functions import XC_ErrorToString
from .capi.errors import XErrorCodes

# error messages corresponding to error codes
_error_messages = {}

class PropertyAccess(IntEnum):
    """
    Property access enumeration.
    """

    READ = 0
    WRITE = 1


def _initialize_error_messages():
    # initialize error messages on import
    for item in XErrorCodes:
        buf = ctypes.create_string_buffer(1024)
        XC_ErrorToString(item.value, buf, 1024)

        _error_messages[item.value] = buf.value.decode()

_initialize_error_messages()


class XenethException(Exception):
    """
    Generic exception class for non SDK errors and base class for exceptions in this package.
    """

    def __init__(self, message: str):
        """
        param message: The error message.
        """
        super().__init__(message)
        self.message = message


class XenethAPIException(XenethException):
    """Raised when an API call returns an error."""

    def __init__(self, error_code: int):
        """
        param error_code: The error code returned by the API call. 
        """

        msg = _error_messages.get(error_code, None)
        super().__init__(msg)

        self.error_code = error_code

class XCameraAccessException(XenethException):
    """Property access violation"""

    def __init__(self, property_name: str, access: PropertyAccess):
        """
        param property_name: The name of the property that causes the exception.
        """

        if access == PropertyAccess.READ:
            super().__init__(f"Property '{property_name}' cannot be read. It is write-only.")
        else:
            super().__init__(f"Property '{property_name}' cannot be written. It is read-only.")

class XCameraInvalidPropertyException(XenethException):
    """
    Raised when trying to access a camera property that does not exist.
    """

    def __init__(self, property_name: str):
        """
        param property_name: The name of the property that does not exist.
        """
        super().__init__(f"Camera property {property_name} does not exist.")

class XCameraInvalidValueException(XenethException):
    """
    Raised when trying to set an invalid value for a camera property.
    For example, an invalid value for en enum property.
    """

    def __init__(self, property_name: str, value: any):
        """
        :param property_name: The name of the property that does not exist.
        :param value: The invalid value.
        """
        super().__init__(f"The value {value} is not valid for property {property_name}.")
