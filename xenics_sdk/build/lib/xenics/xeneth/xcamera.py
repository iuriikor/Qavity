"""
xcamera.py

XenEth camera class
"""

from typing import Any, Union, Tuple

from xenics.xeneth.capi.errors import XErrorCodes
from xenics.xeneth.util import handle_c_call
from xenics.xeneth.util import _log as logger

# too many functions to import without wildcard
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from xenics.xeneth.capi.functions import *
from xenics.xeneth.properties import *
from xenics.xeneth.capi.enums import *
from xenics.xeneth.errors import *


from xenics.xeneth.capi.util import (
    _create_property_category_buffer,
    _create_property_name_buffer,
    _create_property_string_value_buffer,
    _create_property_unit_buffer)

from xenics.xeneth.xframebuffer import XFrameBuffer


# only export XCamera class
__all__ = ['XCamera']

class XCamera(object):
    """
    Represents a XenICs camera.
    """

    _property_types = {
        # map a (subset of the) XPropType to a Property Class
        0x01: NumProp,
        0x02: EnumProp,
        0x04: BoolProp,
        0x08: BlobProp,
        0x10: StringProp,
        0x20: ActionProp,
    }


    def __init__(self) -> None:
        self._name = None
        self._handle = 0
        self._status_cb = ctypes.cast(None, XStatus)
        self._callback_data = None
        self.props = Properties()

        self._native_frame_type = XFrameType.FT_UNKNOWN

    def _populate_props(self):
        """
        Retrieve the properties of the camera and make them available as attributes of the props member object
        """

        numprops = self.get_property_count()

        for i in range(numprops):

            propname  = self.get_property_name(i)
            proptype = self.get_property_type(propname)
            propcategory = self.get_property_category(propname)

            propclass = self._property_types.get(proptype.value & 0xff)

            if propclass:
                prop = propclass(self.handle, propname, proptype, propcategory)

                # Handle the special case where properties end in '(0)', simply strip those 3 characters from the name used as attribute
                if propname.endswith('(0)'):
                    propname = propname[:-3]

                # self._properties.append(prop)
                setattr(self.props, propname, prop)  # .decode bytes->str

    #region Properties

    @property
    def handle(self) -> int:
        """
        The camera handle
        """
        return self._handle

    @property
    def name(self) -> str:
        """
        The name of the camera.
        """
        return self._name

    @property
    def width(self) -> int:
        """
        The frame width of the camera in pixels.
        """
        return XC_GetWidth(self._handle)

    @property
    def height(self) -> int:
        """
        The frame height of the camera in pixels.
        """
        return XC_GetHeight(self._handle)

    @property
    def max_width(self) -> int:
        """
        The frame width of the camera in pixels.
        """
        return XC_GetMaxWidth(self._handle)

    @property
    def max_height(self) -> int:
        """
        The frame height of the camera in pixels.
        """
        return XC_GetMaxHeight(self._handle)

    @property
    def is_initialized(self) -> bool:
        """
        Whether the camera is initialized.
        """
        return XC_IsInitialised(self._handle)

    @property
    def is_capturing(self) -> bool:
        """
        Whether the camera is capturing.
        """
        return XC_IsCapturing(self._handle)

    @property
    def frame_size(self) -> int:
        """
        The frame size in bytes.
        """
        return XC_GetFrameSize(self._handle)

    @property
    def frame_footer_length(self) -> int:
        """
        The length of the frame footer.
        """

        return XC_GetFrameFooterLength(self.handle)

    @property
    def bitsize(self) -> int:
        """
        The bitsize of the camera.
        """
        return XC_GetBitSize(self._handle)

    @property
    def max_value(self) -> int:
        """
        The max value of the camera.
        """
        return XC_GetMaxValue(self._handle)

    @property
    def frame_count(self) -> int:
        """
        The frame size in bytes.
        """
        return XC_GetFrameCount(self._handle)

    @property
    def frame_rate(self) -> int:
        """
        The frame size in bytes.
        """
        return XC_GetFrameRate(self._handle)

    @property
    def frame_type(self) -> XFrameType:
        """
        The frame type.
        """
        return XFrameType(XC_GetFrameType(self._handle))

    @property
    def colour_mode(self) -> ColourMode:
        """
        Gets the current colour mode of the camera.

        :return: The current colour mode.
        """
        return XC_GetColourMode(self._handle)


    @colour_mode.setter
    def colour_mode(self, value: ColourMode) -> None:
        return XC_SetColourMode(self._handle, value)

    #endregion Properties


    def open(self, name: str, status_callback: callable = None, callback_data: any = None) -> bool:
        """
        Opens the camera.

        :param status_callback: Callback function to be called when the camera status changes.
        :param callback_data: User-defined data to be passed to the callback. Can be any Python object, but passed value types are immutable in the callback.

        :return: True if the camera is connected and initialized, otherwise False.
        """

        if status_callback is not None:
            # wrap python function into XStatus callback function pointer
            self._status_cb = XStatus(status_callback)

        # create py_object from callback data
        self._callback_data = ctypes.py_object(callback_data)

        self._name = name
        self._handle = XC_OpenCamera(self._name.encode(), self._status_cb, self._callback_data)

        # store native frame type (assumes that a camera always start with it's native type)
        self._native_frame_type = self.frame_type

        self._populate_props()

        return self.is_initialized

    def close(self) -> None:
        """
        Closes the camera.
        """
        XC_CloseCamera(self._handle)

        # reset handles and pointers
        self._handle = 0
        self._status_cb = ctypes.cast(None, XStatus)
        self._callback_data = None

    def start_capture(self) -> None:
        """
        Starts the camera capture.
        """
        handle_c_call(lambda: XC_StartCapture(self._handle))

    def stop_capture(self) -> None:
        """
        Stops the camera capture.
        """
        handle_c_call(lambda: XC_StopCapture(self._handle))

    def create_buffer(self, frame_type: XFrameType = XFrameType.FT_NATIVE) -> XFrameBuffer:
        """
        Creates a re-useable frame buffer.

        param frame_type: The frame type to use.
        return: The frame buffer in native format.
        """

        # if given frame type is NATIVE, use the type from the camera
        frame_type = self.frame_type if frame_type == XFrameType.FT_NATIVE else frame_type

        return XFrameBuffer(self.width, self.height, frame_type, self.frame_footer_length)


    def get_frame(self, frame_buffer: XFrameBuffer, flags: XGetFrameFlags = 0) -> bool:
        """
        Gets a frame from the camera. The frame type is determined by the frame_buffer parameter.

        :param frame_buffer: The frame buffer to put the frame in. This buffer should be created using the create_buffer method. 
        :param flags: The frame flags.

        :return: True if a frame is available, False otherwise.
        """

        buf = frame_buffer.data.ctypes.data_as(ctypes.POINTER(ctypes.c_char))

        # always provide actual 'image' size, even if we fetch the footer
        err = XC_GetFrame(self._handle, frame_buffer.frame_type, flags, buf, frame_buffer.size)
        # here we create an exception on the rule for throwing exceptions on error
        # when reading frames non-blocking, error E_NO_FRAME is to be expected
        # in that case, we return an empty buffer
        if err == XErrorCodes.I_OK:
            return True
        elif err == XErrorCodes.E_NO_FRAME:
            return False

        # other error code, raise exception
        raise XenethAPIException(err)

    def get_path(self, path_id: XDirectories) -> str:
        """
        Gets the path specified by the path_id.

        :param path_id: The path id.
        :return: The path.
        """

        buffer = ctypes.create_string_buffer(4096)
        handle_c_call(lambda: XC_GetPath(self._handle, path_id.value, buffer, len(buffer)))

        return buffer.value.decode()

    def load_colour_profile(self, filename: str) -> None:
        """
        Loads a colour profile for the camera from a specified file.

        :param filename: The path to the colour profile file to be loaded.
        """
        handle_c_call(lambda: XC_LoadColourProfile(self._handle, filename.encode()))


    def load_calibration(self, filename: str, flags: XLoadCalibrationFlags) -> None:
        """
        Loads a calibration file into the camera.

        :param filename: The path to the calibration file to be loaded.
        :param flags: Flags that determine the behavior of the calibration loading process. Check the `XLoadCalibrationFlags` enumeration for possible values.
        """
        handle_c_call(lambda: XC_LoadCalibration(self._handle, filename.encode(), flags))


    def load_settings(self, filename: str) -> None:
        """
        Loads the camera settings from a file.

        :param filename: The path to the settings file.
        """
        handle_c_call(lambda: XC_LoadSettings(self._handle, filename.encode()))


    def save_settings(self, filename: str) -> None:
        """
        Saves the current camera settings to a file.

        :param filename: The path where the settings file will be saved.
        """
        handle_c_call(lambda: XC_SaveSettings(self._handle, filename.encode()))


    def get_property_count(self) -> int:
        """
        Gets the number of properties on the camera.

        :return: number of properties
        """
        return XC_GetPropertyCount(self.handle)

    def has_property(self, property_name: str):
        """
        Tests whether a property exists on the camera.

        Note: this method tests for properties in the camera's property system, not actual python properties.
        """

        # Handle the special case where properties end in '(0)', simply strip those 3 characters from the name used as attribute
        if property_name.endswith('(0)'):
            property_name = property_name[:-3]

        try:
            return hasattr(self.props, property_name)
        except XCameraInvalidPropertyException:
            return False


    def get_property_name(self, idx : int) -> str:
        """
        :param idx: The index of the property name to retrieve
        :return: The property name
        """
        property_name = _create_property_name_buffer()
        handle_c_call(lambda:  XC_GetPropertyName(self.handle, idx, property_name, len(property_name)))

        return property_name.value.decode()

    def get_property_category(self, property_name : str) -> str:
        """
        :param property_name: The name of the property for which to retrieve the category
        :return: The property category
        """
        property_category = _create_property_category_buffer()
        handle_c_call(lambda: XC_GetPropertyCategory(self.handle, property_name.encode(), property_category, len(property_category)))

        return property_category.value.decode()

    def get_property_type(self, property_name: str) -> XPropType:
        """
        Gets a discovery system property type

        :param property_name: The name of the property for which to retrieve the value
        :return: The property type
        """
        value = ctypes.c_int()

        handle_c_call(lambda: XC_GetPropertyType(self.handle, property_name.encode(), ctypes.byref(value)))

        return XPropType(value.value)

    def get_property_unit(self, property_name : str) -> str:
        """
        Retrieves the unit of a specified property of the camera.

        :param property_name: The name of the property for which the unit is to be retrieved.

        :return: The unit of the property.
        """
        property_unit = _create_property_unit_buffer()
        handle_c_call(lambda:  XC_GetPropertyUnit(self.handle, property_name.encode(), property_unit, len(property_unit)))

        return property_unit.value.decode()


    def get_property_value(self, property_name: str) -> Union[str, int, float]:
        """
        Retrieves the current value of a specified property of the camera.

        :param property_name: The name of the property for which the value is to be retrieved.

        :return: The current value of the property.
        """
        return self.props[property_name].get()

    def set_property_value(self, property_name: str, value: Any) -> None:
        """
        Sets the value of a specified property of the camera.

        :param property_name: The name of the property for which the value is to be set.
        :param value: The new value for the property.
        """
        self.props[property_name].set(value)


    def get_property_range(self, property_name: str) -> Union[Tuple[int, int],Tuple[float, float],Tuple[str, str]]:
        """
        Gets the range of a property.

        :param property_name: The name of the property for which to retrieve the range
        :return: The range. 
        
        For enum properties a tuple of strings is returned, for number a tuple of min,max values is returned.
        For all other property types None is returned.
        """
        range_len = 4096
        proprange = ctypes.create_string_buffer(range_len)

        # get property type
        proptype = self.get_property_type(property_name)

        if proptype & XPropType.XType_Base_Number == XPropType.XType_Base_Number:
            handle_c_call(lambda: XC_GetPropertyRange(self.handle, property_name.encode(), proprange, range_len))

            # TODO: check if this is correct
            # Got an empty string on a Number property (PixelFormatChanged on GoBi camera)
            if proprange.value.decode() == "":
                return None

            items = proprange.value.decode().split(">")

            try:
                # first try hex format
                return (int(items[0],16), int(items[1],16))
            except ValueError:
                return (float(items[0]), float(items[1]))

        elif proptype & XPropType.XType_Base_Enum == XPropType.XType_Base_Enum:
            handle_c_call(lambda: XC_GetPropertyRangeE(self.handle, property_name.encode(), proprange, range_len))
            items = proprange.value.decode().split(",")

            # each item contains the enum value and UI value/description
            # only return the enum values
            return [i.split("=")[0] for i in items]

        return None

    
    def save_data(self, filename: str, flags: XSaveDataFlags) -> None:
        """
        Saves the data in XPNG format, including thermal metadata

        :param filename: path of the file to save
        :param flags: Combination of XSaveDataFlags values
        """
        handle_c_call(lambda: XC_SaveData(self._handle, filename.encode(), flags))

    def add_image_filter(self, filter_func: callable, user_param: Any) -> int:
        """
        Add a custom image filter to the camera.

        :param filter_func: The filter function
        :param user_param: The user parameter to pass to the filter
        :return: The ID of the added filter
        """

        # cam argument is unused for now. Underscore keeps pylint silent
        def filter_wrapper(_cam, user_param, msg, p_msg_param):

            # TODO: check if this is the right way to do this
            # for now, ignore camera pointer and assume the camera is always self
            # handle = XC_CameraToHandle(cam)

            return filter_func(self, user_param, XFilterMessage(msg), p_msg_param)


        fid = XC_AddImageFilter(self.handle, XImageFilter(filter_wrapper), user_param)

        return fid

    def is_filter_running(self, filter_id: int) -> bool:
        """
        Checks if a filter is running.

        :param filter_id: The ID of the filter
        :return: True if the filter is running, False otherwise
        """
        return bool(XC_IsFilterRunning(self.handle, filter_id))

    def pri_image_filter(self, filter_id: int, prio: int) -> None:
        """
        Prioritizes an image filter.

        :param filter_id: The ID of the filter
        :param prio: The priority of the filter
        """
        XC_PriImageFilter(self.handle, filter_id, prio)

    def rem_image_filter(self, filter_id: int) -> None:
        """
        Removes an image filter.

        :param filter_id: The ID of the filter
        """
        XC_RemImageFilter(self.handle, filter_id)

    def filter_get_list(self) -> list[str]:
        """
        Returns a list of filter names.

        :param fltlistmax: The maximum length of the filter list
        :return: A list of filter names
        """
        fltlist = ctypes.create_string_buffer(2048)
        handle_c_call( lambda: XC_FLT_GetFilterList(self.handle, fltlist, 2048))

        return fltlist.value.decode().split(',')

    def filter_queue(self, filter_name: str, filter_params: str = "") -> int:
        """
        Queues a filter.

        :param fltname: The name of the filter to be queued
        :param fltparms: The parameters of the filter
        :return: The ID of the queued filter
        """
        filter_id = XC_FLT_Queue(self.handle, filter_name.encode(), filter_params.encode())
        if filter_id == -1:
            raise XenethException("Error queueing filter")

        return filter_id

    def filter_adu_to_temperature(self, filter_id: int, adu: int) -> float:
        """Converts ADU to temperature"""
        temp = ctypes.c_double()
        handle_c_call( lambda: XC_FLT_ADUToTemperature(self.handle, filter_id, adu, ctypes.byref(temp)))

        return temp.value

    def filter_adu_to_temperature_lin(self, filter_id: int, adu: int) -> float:
        """Converts ADU to temperature linear"""
        temp = ctypes.c_double()
        handle_c_call( lambda: XC_FLT_ADUToTemperatureLin(self.handle, filter_id, adu, ctypes.byref(temp)))

        return temp.value
    
    def filter_temperature_to_adu(self, filter_id: int, temp: float) -> int:
        """Converts temperature to ADU"""
        adu = ctypes.c_ulong()
        handle_c_call( lambda: XC_FLT_TemperatureToADU(self.handle, filter_id, temp, ctypes.byref(adu)))

        return adu.value

    def filter_temperature_to_adu_lin(self, filter_id: int, temp: float) -> int:
        """Converts temperature to ADU linear"""
        adu = ctypes.c_ulong()
        handle_c_call( lambda: XC_FLT_TemperatureToADU(self.handle, filter_id, temp, ctypes.byref(adu)))

        return adu.value

    def filter_send_stream(self, filter_id: int, msg: XFilterMessage, stream: bytes) -> None:
        """
        Sends a stream of data to a specified filter. 

        :param filter_id: Identifier for the filter to which the stream will be sent.
        :param msg: Type of message to be sent.
        :param stream: Stream of data to be sent.
        """
        handle_c_call(lambda: XC_FLT_SendStream(self._handle, filter_id, msg, stream.encode(), len(stream)))

    def filter_recv_stream(self, filter_id: int, msg: XFilterMessage) -> str:
        """Receive stream from the filter"""

        # first check required length by passing null pointer
        buf_len = ctypes.c_int(-1)
        handle_c_call(lambda: XC_FLT_RecvStream(self.handle, filter_id, msg, None, ctypes.byref(buf_len)))

        buf = ctypes.create_string_buffer(buf_len.value)
        handle_c_call(lambda: XC_FLT_RecvStream(self.handle, filter_id, msg, buf, ctypes.byref(buf_len)))

        return buf.value.decode()

    def filter_set_parameter(self, filter_id: int, parameter: str, value: str) -> None:
        """
        Sets a filter parameter value

        :param filter_id: Filter ID/handle from queue_filter method
        :param parameter: Parameter name
        :param value: The value to set
        """
        handle_c_call(lambda: XC_FLT_SetParameter(self.handle, filter_id, parameter.encode(), value.encode()))

    def filter_get_parameter(self, filter_id: int, parameter: str) -> str:
        """
        Gets a filter parameter value

        :param filter_id: Filter ID/handle from queue_filter method
        :param parameter: Parameter name

        :return: The value of the parameter
        """
        value = _create_property_string_value_buffer()
        value_len = ctypes.c_int(len(value))
        handle_c_call(lambda: XC_FLT_GetParameter(self.handle, filter_id, parameter.encode(), value, ctypes.byref(value_len)))

        return value.value.decode()
    

    