"""
discovery.py

Functions related to device discovery
"""

import ctypes
from typing import Any, Tuple, Union
from xenics.xeneth.capi.enums import XEnumerationFlags, XPropType
from xenics.xeneth.capi.structs import XDeviceInformation

from xenics.xeneth.capi.util import (
    _create_property_category_buffer,
    _create_property_name_buffer,
    _create_property_string_value_buffer)


from xenics.xeneth.capi.functions import (
    XCD_EnumerateDevices, XCD_GetPropertyCategory,
    XCD_GetPropertyCount, XCD_GetPropertyName,
    XCD_GetPropertyRange, XCD_GetPropertyType,
    XCD_GetPropertyValue, XCD_GetPropertyValueL,
    XCD_SetPropertyValue, XCD_SetPropertyValueL
    )

from xenics.xeneth.util import handle_c_call


__all__ = ['enumerate_devices', 'get_property_count', 'get_property_name', 'get_property_category',
           'get_property_value', 'set_property_value', 'get_property_range', 'get_property_type',
           'XEnumerationFlags', 'XDeviceInformation', 'XPropType' ]

def enumerate_devices(flags:int=XEnumerationFlags.XEF_EnableAll) -> Tuple[XDeviceInformation,...]:
    """
    Enumerates all Xeneth connected devices.

    :param flags: bitwise combination of XEnumerationFlags
    :return: tuple of XDeviceInformation (for each discovered device)
    """

    count = ctypes.c_uint32()

    # count devices
    handle_c_call(lambda: XCD_EnumerateDevices( None, ctypes.byref(count), flags))

    dev_info = (XDeviceInformation * count.value)()
    handle_c_call(lambda: XCD_EnumerateDevices(dev_info, count, XEnumerationFlags.XEF_UseCached))

    return [d for d in dev_info]

def get_property_count() -> int:
    """
    Gets the number of properties on the discovery system.

    :return: number of properties
    """
    return XCD_GetPropertyCount()

def get_property_name(idx : int) -> str:
    """
    :param idx: The index of the property name to retrieve
    :return: The property name
    """
    property_name = _create_property_name_buffer()
    handle_c_call(lambda:  XCD_GetPropertyName( idx, property_name, len(property_name)))

    return property_name.value.decode()

def get_property_category(property_name : str) -> str:
    """
    :param property_name: The name of the property for which to retrieve the category
    :return: The property category
    """
    property_category = _create_property_category_buffer()
    handle_c_call(lambda: XCD_GetPropertyCategory( property_name.encode(), property_category, len(property_category)))

    return property_category.value.decode()

def _get_property_value_str(property_name: str) -> str:
    """
    Gets a discovery system property value in string format

    :param property_name: The name of the property for which to retrieve the value
    :return: The property value
    """
    value = _create_property_string_value_buffer()
    handle_c_call(lambda: XCD_GetPropertyValue( property_name.encode(), value, len(value)))

    return value.value.decode()

def _get_property_value_l(property_name: str) -> int:
    """
    Gets a discovery system property value in int (long) format

    :param property_name: The name of the property for which to retrieve the value
    :return: The property value
    """
    value = ctypes.c_int()
    handle_c_call(lambda: XCD_GetPropertyValueL(property_name.encode(), ctypes.byref(value)))

    return value.value

def _set_property_value_str(property_name: str, value: str):
    """
    Sets a discovery system property value in string format

    :param property_name: The name of the property for which to set the value
    :param value: The value to set
    """
    handle_c_call(lambda: XCD_SetPropertyValue( property_name.encode(), value.encode(), len(value)))

def _set_property_value_l(property_name: str, value: int):
    """
    Sets a discovery system property value in int (long) format

    :param property_name: The name of the property for which to set the value
    :param value: The value to set
    """
    handle_c_call(lambda: XCD_SetPropertyValueL(property_name.encode(), value))

def get_property_value(property_name: str) -> Any:
    """
    Gets a discovery system property value.

    :param property_name: The name of the property for which to retrieve the value
    :return: The property value
    """

    proptype = get_property_type(property_name)

    if proptype & XPropType.XType_Base_String == XPropType.XType_Base_String:
        return _get_property_value_str(property_name)
    elif proptype & XPropType.XType_Base_Number == XPropType.XType_Base_Number:
        return _get_property_value_l(property_name)
    elif proptype & XPropType.XType_Base_Enum == XPropType.XType_Base_Enum:
        return _get_property_value_str(property_name)

def set_property_value(property_name: str, value: Any):
    """
    Sets a discovery system property value.

    :param property_name: The name of the property for which to set the value
    :param value: The value to set
    """
    proptype = get_property_type(property_name)

    if proptype & XPropType.XType_Base_String == XPropType.XType_Base_String:
        _set_property_value_str(property_name, value)
    elif proptype & XPropType.XType_Base_Number == XPropType.XType_Base_Number:
        _set_property_value_l(property_name, value)
    elif proptype & XPropType.XType_Base_Enum == XPropType.XType_Base_Enum:
        _set_property_value_str(property_name, value)

def get_property_type(property_name: str) -> XPropType:
    """
    Gets a discovery system property type

    :param property_name: The name of the property for which to retrieve the value
    :return: The property type
    """
    value = ctypes.c_int()

    handle_c_call(lambda: XCD_GetPropertyType(property_name.encode(), ctypes.byref(value)))

    return XPropType(value.value)

def get_property_range(property_name: str) -> Union[Tuple[int, int],Tuple[str, str]]:
    """
    Gets the range of a discovery system property.

    :param property_name: The name of the property for which to retrieve the range
    :return: The range. 
    
    For enum properties a tuple of strings is returned, for number a tuple of min,max values is returned.
    For all other property types None is returned.
    """
    range_len = 256
    proprange = ctypes.create_string_buffer(range_len)

    handle_c_call(lambda: XCD_GetPropertyRange(property_name.encode(), proprange, range_len))

    # get property type
    proptype = get_property_type(property_name)

    if proptype & XPropType.XType_Base_Number == XPropType.XType_Base_Number:
        items = proprange.value.decode().split(">")
        return (int(items[0]), int(items[1]))
    elif proptype & XPropType.XType_Base_Enum == XPropType.XType_Base_Enum:
        return tuple(proprange.value.decode().split(","))

    return None
