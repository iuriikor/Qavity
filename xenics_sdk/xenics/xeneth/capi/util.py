"""
XenEth C API util functions
"""

import ctypes
import logging

# define buffer sizes
MAX_PROPERTY_NAME_LENGTH = 256
MAX_PROPERTY_UNIT_LENGTH = 256
MAX_PROPERTY_CATEGORY_LENGTH = 1024
MAX_PROPERTY_STRING_VALUE_LENGTH = 1024
MAX_PROPERTY_ENUM_VALUE_LENGTH = 1024

# functions to create buffers according to buffer sizes
def _create_property_name_buffer():
    return ctypes.create_string_buffer(MAX_PROPERTY_NAME_LENGTH)

def _create_property_category_buffer():
    return ctypes.create_string_buffer(MAX_PROPERTY_CATEGORY_LENGTH)

def _create_property_string_value_buffer():
    return ctypes.create_string_buffer(MAX_PROPERTY_STRING_VALUE_LENGTH)

def _create_property_enum_value_buffer():
    return ctypes.create_string_buffer(MAX_PROPERTY_ENUM_VALUE_LENGTH)

def _create_property_unit_buffer():
    return ctypes.create_string_buffer(MAX_PROPERTY_UNIT_LENGTH)

# create logger
_log = logging.getLogger("xenics.xeneth.capi")
_log.addHandler(logging.NullHandler())
_log.propagate = False
