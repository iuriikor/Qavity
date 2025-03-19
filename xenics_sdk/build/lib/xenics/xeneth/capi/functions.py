"""
functions.py

Defines C API function imports.
"""

import ctypes

from xenics.xeneth.capi.structs import XDeviceInformation

# import dll
from xenics.xeneth.capi import xenethdll

# -----------------------
# XCD Discovery Functions
# -----------------------


# ErrCode XCD_EnumerateDevices(XDeviceInformation * const deviceInformation, unsigned int * const deviceCount, XEnumerationFlags flags)
XCD_EnumerateDevices = getattr(xenethdll, 'XCD_EnumerateDevices')
XCD_EnumerateDevices.argtypes = [ctypes.POINTER(XDeviceInformation), ctypes.POINTER(ctypes.c_ulong), ctypes.c_long]
XCD_EnumerateDevices.restype = ctypes.c_ulong

# dword XCD_GetPropertyCount(void)
XCD_GetPropertyCount = getattr(xenethdll, 'XCD_GetPropertyCount')
XCD_GetPropertyCount.argtypes = []
XCD_GetPropertyCount.restype = ctypes.c_long

# ErrCode XCD_GetPropertyName(dword idx, char * propertyName, dword maxLen)
XCD_GetPropertyName = getattr(xenethdll, 'XCD_GetPropertyName')
XCD_GetPropertyName.argtypes = [ctypes.c_uint, ctypes.c_char_p, ctypes.c_uint]
XCD_GetPropertyName.restype = ctypes.c_ulong

# ErrCode XCD_GetPropertyCategory(const char * propertyName, char * propertyCategory, int maxLen)
XCD_GetPropertyCategory = getattr(xenethdll, 'XCD_GetPropertyCategory')
XCD_GetPropertyCategory.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
XCD_GetPropertyCategory.restype = ctypes.c_ulong


# ErrCode XCD_GetPropertyValue(const char * propertyName, char * value, dword maxLen)
XCD_GetPropertyValue = getattr(xenethdll, 'XCD_GetPropertyValue')
XCD_GetPropertyValue.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
XCD_GetPropertyValue.restype = ctypes.c_ulong

# ErrCode XCD_GetPropertyValueL(const char * propertyName, int * value)
XCD_GetPropertyValueL = getattr(xenethdll, 'XCD_GetPropertyValueL')
XCD_GetPropertyValueL.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
XCD_GetPropertyValueL.restype = ctypes.c_ulong


# ErrCode XCD_SetPropertyValue(const char * propertyName, const char * value, dword len)
XCD_SetPropertyValue = getattr(xenethdll, 'XCD_SetPropertyValue')
XCD_SetPropertyValue.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
XCD_SetPropertyValue.restype = ctypes.c_ulong

# ErrCode XCD_SetPropertyValueL(const char * propertyName, int value)
XCD_SetPropertyValueL = getattr(xenethdll, 'XCD_SetPropertyValueL')
XCD_SetPropertyValueL.argtypes = [ctypes.c_char_p, ctypes.c_int]
XCD_SetPropertyValueL.restype = ctypes.c_ulong


# ErrCode XCD_GetPropertyType(const char * propertyName, XPropType * propertyType)
XCD_GetPropertyType = getattr(xenethdll, 'XCD_GetPropertyType')
XCD_GetPropertyType.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
XCD_GetPropertyType.restype = ctypes.c_ulong


# ErrCode XCD_GetPropertyRange(const char * propertyName, char * const range, int maxLen)
XCD_GetPropertyRange = getattr(xenethdll, 'XCD_GetPropertyRange')
XCD_GetPropertyRange.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
XCD_GetPropertyRange.restype = ctypes.c_ulong



#--------------------
# XC Camera functions
#--------------------

# # int XC_ErrorToString (ErrCode e, char * dst, int len)
XC_ErrorToString = getattr(xenethdll, 'XC_ErrorToString')
XC_ErrorToString.argtypes = [ctypes.c_ulong, ctypes.c_char_p, ctypes.c_int]
XC_ErrorToString.restype = ctypes.c_int

# Status callback prototype
XStatus = ctypes.CFUNCTYPE(ctypes.c_ulong, ctypes.py_object, ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong)

# XCHANDLE XC_CameraToHandle (voidp cam)
XC_CameraToHandle = getattr(xenethdll, 'XC_CameraToHandle')
XC_CameraToHandle.argtypes = [ctypes.c_void_p]
XC_CameraToHandle.restype = ctypes.c_void_p

# dword XC_GetWidth (XCHANDLE h)
XC_GetWidth = getattr(xenethdll, 'XC_GetWidth')
XC_GetWidth.argtypes = [ctypes.c_int]
XC_GetWidth.restype = ctypes.c_ulong

# dword XC_GetHeight (XCHANDLE h)
XC_GetHeight = getattr(xenethdll, 'XC_GetHeight')
XC_GetHeight.argtypes = [ctypes.c_int]
XC_GetHeight.restype = ctypes.c_ulong

# dword XC_GetMaxWidth (XCHANDLE h)
XC_GetMaxWidth = getattr(xenethdll, 'XC_GetMaxWidth')
XC_GetMaxWidth.argtypes = [ctypes.c_int]
XC_GetMaxWidth.restype = ctypes.c_ulong

# dword XC_GetMaxHeight (XCHANDLE h)
XC_GetMaxHeight = getattr(xenethdll, 'XC_GetMaxHeight')
XC_GetMaxHeight.argtypes = [ctypes.c_int]
XC_GetMaxHeight.restype = ctypes.c_ulong

# XCHANDLE XC_OpenCamera (const char * pCameraName, XStatus pCallBack, void * pUser)
XC_OpenCamera = getattr(xenethdll, 'XC_OpenCamera')
XC_OpenCamera.argtypes = [ctypes.c_char_p, XStatus, ctypes.py_object]
XC_OpenCamera.restype = ctypes.c_int

# void XC_CloseCamera (XCHANDLE hnd)
XC_CloseCamera = getattr(xenethdll, 'XC_CloseCamera')
XC_CloseCamera.argtypes = [ctypes.c_int]
XC_CloseCamera.restype = None

# boole XC_IsInitialised (XCHANDLE h)
XC_IsInitialised = getattr(xenethdll, 'XC_IsInitialised')
XC_IsInitialised.argtypes = [ctypes.c_int]
XC_IsInitialised.restype = ctypes.c_bool

# boole XC_IsCapturing (XCHANDLE h)
XC_IsCapturing = getattr(xenethdll, 'XC_IsCapturing')
XC_IsCapturing.argtypes = [ctypes.c_int]
XC_IsCapturing.restype = bool

# ErrCode XC_StartCapture (XCHANDLE h)
XC_StartCapture = getattr(xenethdll, 'XC_StartCapture')
XC_StartCapture.argtypes = [ctypes.c_int]
XC_StartCapture.restype = ctypes.c_ulong

# ErrCode XC_StopCapture (XCHANDLE h)
XC_StopCapture = getattr(xenethdll, 'XC_StopCapture')
XC_StopCapture.argtypes = [ctypes.c_int]
XC_StopCapture.restype = ctypes.c_ulong

# dword XC_GetFrameSize (XCHANDLE h)
XC_GetFrameSize = getattr(xenethdll, 'XC_GetFrameSize')
XC_GetFrameSize.argtypes = [ctypes.c_int]
XC_GetFrameSize.restype = ctypes.c_uint

# FrameType XC_GetFrameType (XCHANDLE h)
XC_GetFrameType = getattr(xenethdll, 'XC_GetFrameType')
XC_GetFrameType.argtypes = [ctypes.c_int]
XC_GetFrameType.restype = ctypes.c_int

# dword XC_GetMaxValue (XCHANDLE h)
XC_GetMaxValue = getattr(xenethdll, 'XC_GetMaxValue')
XC_GetMaxValue.argtypes = [ctypes.c_int]
XC_GetMaxValue.restype = ctypes.c_uint

# ErrCode XC_GetFrame(XCHANDLE h, FrameType type, unsigned long ulFlags, void * buffer, unsigned int size)
XC_GetFrame = getattr(xenethdll, 'XC_GetFrame')
XC_GetFrame.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_uint]
XC_GetFrame.restype = ctypes.c_ulong

# dword XC_GetFrameCount (XCHANDLE h)
XC_GetFrameCount = getattr(xenethdll, 'XC_GetFrameCount')
XC_GetFrameCount.argtypes = [ctypes.c_int]
XC_GetFrameCount.restype = ctypes.c_uint

# double XC_GetFrameRate (XCHANDLE h)
XC_GetFrameRate = getattr(xenethdll, 'XC_GetFrameRate')
XC_GetFrameRate.argtypes = [ctypes.c_int]
XC_GetFrameRate.restype = ctypes.c_double

# void XC_SetColourMode (XCHANDLE h, ColourMode mode)
XC_SetColourMode = getattr(xenethdll, 'XC_SetColourMode')
XC_SetColourMode.argtypes = [ctypes.c_int, ctypes.c_int]
XC_SetColourMode.restype = None

# ColourMode XC_GetColourMode (XCHANDLE h)
XC_GetColourMode = getattr(xenethdll, 'XC_GetColourMode')
XC_GetColourMode.argtypes = [ctypes.c_int]
XC_GetColourMode.restype = ctypes.c_int

# byte XC_GetBitSize (XCHANDLE h)
XC_GetBitSize = getattr(xenethdll, 'XC_GetBitSize')
XC_GetBitSize.argtypes = [ctypes.c_int]
XC_GetBitSize.restype = ctypes.c_byte

# void XC_Blit (XCHANDLE h, void * w, int x, int y, int width, int height, BlitType type);
XC_Blit = getattr(xenethdll, 'XC_Blit')
XC_Blit.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
XC_Blit.restype = None

# voidp XC_GetFilterFrame (XCHANDLE h)
XC_GetFilterFrame = getattr(xenethdll, 'XC_GetFilterFrame')
XC_GetFilterFrame.argtypes = [ctypes.c_int]
XC_GetFilterFrame.restype = ctypes.c_void_p

# ErrCode XC_LoadColourProfile (XCHANDLE h, const char * p_cFileName)
XC_LoadColourProfile = getattr(xenethdll, 'XC_LoadColourProfile')
XC_LoadColourProfile.argtypes = [ctypes.c_int, ctypes.c_char_p]
XC_LoadColourProfile.restype = ctypes.c_ulong

# ErrCode XC_LoadSettings (XCHANDLE h, const char * p_cFileName)
XC_LoadSettings = getattr(xenethdll, 'XC_LoadSettings')
XC_LoadSettings.argtypes = [ctypes.c_int, ctypes.c_char_p]
XC_LoadSettings.restype = ctypes.c_ulong

# ErrCode XC_SaveSettings (XCHANDLE h, const char * p_cFileName)
XC_SaveSettings = getattr(xenethdll, 'XC_SaveSettings')
XC_SaveSettings.argtypes = [ctypes.c_int, ctypes.c_char_p]
XC_SaveSettings.restype = ctypes.c_ulong

# ErrCode XC_GetPath (XCHANDLE h, int iPath, char * pPath, int iMaxLen);
XC_GetPath = getattr(xenethdll, 'XC_GetPath')
XC_GetPath.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
XC_GetPath.restype = ctypes.c_ulong

# int XC_GetPropertyCount (XCHANDLE h)
XC_GetPropertyCount = getattr(xenethdll, 'XC_GetPropertyCount')
XC_GetPropertyCount.argtypes = [ctypes.c_int]
XC_GetPropertyCount.restype = ctypes.c_int

# ErrCode XC_GetPropertyName(XCHANDLE h, int iIndex, char * pPropName, int iMaxLen)
XC_GetPropertyName = getattr(xenethdll, 'XC_GetPropertyName')
XC_GetPropertyName.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
XC_GetPropertyName.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyRange (XCHANDLE h, const char * pPrp, char * pRange, int iMaxLen)
XC_GetPropertyRange = getattr(xenethdll, 'XC_GetPropertyRange')
XC_GetPropertyRange.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
XC_GetPropertyRange.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyRangeL (XCHANDLE h, const char * pPrp, long * pLow, long * pHigh)
XC_GetPropertyRangeL = getattr(xenethdll, 'XC_GetPropertyRangeL')
XC_GetPropertyRangeL.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]
XC_GetPropertyRangeL.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyRangeF (XCHANDLE h, const char * pPrp, double * pLow, double * pHigh)
XC_GetPropertyRangeF = getattr(xenethdll, 'XC_GetPropertyRangeF')
XC_GetPropertyRangeF.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
XC_GetPropertyRangeF.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyRangeE(XCHANDLE h, const char * pPrp, char * pRange, int iMaxLen)
XC_GetPropertyRangeE = getattr(xenethdll, 'XC_GetPropertyRangeE')
XC_GetPropertyRangeE.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
XC_GetPropertyRangeE.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyType(XCHANDLE h, const char * pPrp, XPropType * pPropType)
XC_GetPropertyType = getattr(xenethdll, 'XC_GetPropertyType')
XC_GetPropertyType.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
XC_GetPropertyType.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyCategory(XCHANDLE h, const char * pPrp, char * pCategory, int iMaxLen)
XC_GetPropertyCategory = getattr(xenethdll, 'XC_GetPropertyCategory')
XC_GetPropertyCategory.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
XC_GetPropertyCategory.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyUnit (XCHANDLE h, const char * pPrp, char * pUnit, int iMaxLen)
XC_GetPropertyUnit = getattr(xenethdll, 'XC_GetPropertyUnit')
XC_GetPropertyUnit.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
XC_GetPropertyUnit.restype = ctypes.c_ulong

# ErrCode XC_SetPropertyValue (XCHANDLE h, const char * pPrp, const char * pValue, const char * pUnit)
XC_SetPropertyValue = getattr(xenethdll, 'XC_SetPropertyValue')
XC_SetPropertyValue.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
XC_SetPropertyValue.restype = ctypes.c_ulong

# ErrCode XC_SetPropertyValueL (XCHANDLE h, const char * pPrp, long lValue, const char * pUnit)
XC_SetPropertyValueL = getattr(xenethdll, 'XC_SetPropertyValueL')
XC_SetPropertyValueL.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_long, ctypes.c_char_p]
XC_SetPropertyValueL.restype = ctypes.c_ulong

# ErrCode XC_SetPropertyValueF(XCHANDLE h, const char * pPrp, double dValue, const char * pUnit)
XC_SetPropertyValueF = getattr(xenethdll, 'XC_SetPropertyValueF')
XC_SetPropertyValueF.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_double, ctypes.c_char_p]
XC_SetPropertyValueF.restype = ctypes.c_ulong

# ErrCode XC_SetPropertyValueE(XCHANDLE h, const char * pPrp, const char * pValue)
XC_SetPropertyValueE = getattr(xenethdll, 'XC_SetPropertyValueE')
XC_SetPropertyValueE.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
XC_SetPropertyValueE.restype = ctypes.c_ulong

# ErrCode XC_SetPropertyBlob (XCHANDLE h, const char * pPrp, const char * pValue, unsigned int len)
XC_SetPropertyBlob = getattr(xenethdll, 'XC_SetPropertyBlob')
XC_SetPropertyBlob.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
XC_SetPropertyBlob.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyValue(XCHANDLE h, const char * pPrp, char * pValue, int iMaxLen)
XC_GetPropertyValue = getattr(xenethdll, 'XC_GetPropertyValue')
XC_GetPropertyValue.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
XC_GetPropertyValue.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyValueL(XCHANDLE h, const char * pPrp, long * pValue)
XC_GetPropertyValueL = getattr(xenethdll, 'XC_GetPropertyValueL')
XC_GetPropertyValueL.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_long)]
XC_GetPropertyValueL.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyValueF(XCHANDLE h, const char * pPrp, double * pValue)
XC_GetPropertyValueF = getattr(xenethdll, 'XC_GetPropertyValueF')
XC_GetPropertyValueF.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
XC_GetPropertyValueF.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyValueE (XCHANDLE h, const char * pPrp, char * pValue, int iMaxLen)
XC_GetPropertyValueE = getattr(xenethdll, 'XC_GetPropertyValueE')
XC_GetPropertyValueE.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
XC_GetPropertyValueE.restype = ctypes.c_ulong

# ErrCode XC_GetPropertyBlob (XCHANDLE h, const char * pPrp, char * pValue, unsigned int len)
XC_GetPropertyBlob = getattr(xenethdll, 'XC_GetPropertyBlob')
XC_GetPropertyBlob.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
XC_GetPropertyBlob.restype = ctypes.c_ulong

# ErrCode XC_LoadCalibration (XCHANDLE h, const char * p_cFileName, unsigned long ulFlags)
XC_LoadCalibration = getattr(xenethdll, 'XC_LoadCalibration')
XC_LoadCalibration.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_ulong]
XC_LoadCalibration.restype = ctypes.c_ulong

# ErrCode XC_SaveData (XCHANDLE h, const char * p_cFileName, unsigned long ulFlags)
XC_SaveData = getattr(xenethdll, 'XC_SaveData')
XC_SaveData.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_ulong]
XC_SaveData.restype = ctypes.c_ulong

#--------
# Filters
#--------

# typedef ErrCode (CALLCVCB *XImageFilter)(void * v_pCamera, void * v_pUserParm, XFilterMessage tMsg, void * v_pMsgParm)
XImageFilter = ctypes.CFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p, ctypes.py_object, ctypes.c_int, ctypes.c_void_p)

# ErrCode XC_FLT_GetFilterList(XCHANDLE hnd, char *fltlist, int fltlistmax)
XC_FLT_GetFilterList = getattr(xenethdll, 'XC_FLT_GetFilterList')
XC_FLT_GetFilterList.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
XC_FLT_GetFilterList.restype = ctypes.c_ulong

# FilterID XC_FLT_Queue(XCHANDLE hnd, const char *fltname, const char *fltparms)
XC_FLT_Queue = getattr(xenethdll, 'XC_FLT_Queue')
XC_FLT_Queue.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
XC_FLT_Queue.restype = ctypes.c_ulong

# boole XC_IsFilterRunning(XCHANDLE h, FilterID fid)
XC_IsFilterRunning = getattr(xenethdll, 'XC_IsFilterRunning')
XC_IsFilterRunning.argtypes = [ctypes.c_int, ctypes.c_ulong]
XC_IsFilterRunning.restype = ctypes.c_bool

# void XC_PriImageFilter(XCHANDLE h, FilterID fid, int prio)
XC_PriImageFilter = getattr(xenethdll, 'XC_PriImageFilter')
XC_PriImageFilter.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_int]
XC_PriImageFilter.restype = None

# boole XC_IsFilterRunning(XCHANDLE h, FilterID fid)
XC_IsFilterRunning = getattr(xenethdll, 'XC_IsFilterRunning')
XC_IsFilterRunning.argtypes = [ctypes.c_int, ctypes.c_ulong]
XC_IsFilterRunning.restype = ctypes.c_bool

# void XC_RemImageFilter(XCHANDLE h, FilterID fid)
XC_RemImageFilter = getattr(xenethdll, 'XC_RemImageFilter')
XC_RemImageFilter.argtypes = [ctypes.c_int, ctypes.c_int]
XC_RemImageFilter.restype = None

# double XC_FLT_GetTValue(XCHANDLE hnd, FilterID fid, double e, dword x, dword y)
XC_FLT_GetTValue = getattr(xenethdll, 'XC_FLT_GetTValue')
XC_FLT_GetTValue.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_ulong, ctypes.c_ulong]
XC_FLT_GetTValue.restype = ctypes.c_double

# double XC_FLT_GetValue(XCHANDLE hnd, FilterID fid, dword x, dword y)
XC_FLT_GetValue = getattr(xenethdll, 'XC_FLT_GetValue')
XC_FLT_GetValue.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong]
XC_FLT_GetValue.restype = ctypes.c_double

# ErrCode XC_FLT_ADUToTemperature(XCHANDLE hnd, FilterID fid, dword adu, double * temp)
XC_FLT_ADUToTemperature = getattr(xenethdll, 'XC_FLT_ADUToTemperature')
XC_FLT_ADUToTemperature.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_ulong, ctypes.POINTER(ctypes.c_double)]
XC_FLT_ADUToTemperature.restype = ctypes.c_ulong

# ErrCode XC_FLT_TemperatureToADU(XCHANDLE hnd, FilterID fid, double temp, dword * adu)
XC_FLT_TemperatureToADU = getattr(xenethdll, 'XC_FLT_TemperatureToADU')
XC_FLT_TemperatureToADU.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_ulong)]
XC_FLT_TemperatureToADU.restype = ctypes.c_ulong

# ErrCode XC_FLT_ADUToTemperatureLin(XCHANDLE hnd, FilterID fid, dword adu, double * temp)
XC_FLT_ADUToTemperatureLin = getattr(xenethdll, 'XC_FLT_ADUToTemperatureLin')
XC_FLT_ADUToTemperatureLin.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_ulong, ctypes.POINTER(ctypes.c_double)]
XC_FLT_ADUToTemperatureLin.restype = ctypes.c_ulong

# ErrCode XC_FLT_TemperatureToADULin(XCHANDLE hnd, FilterID fid, double temp, dword * adu)
XC_FLT_TemperatureToADULin = getattr(xenethdll, 'XC_FLT_TemperatureToADULin')
XC_FLT_TemperatureToADULin.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.POINTER(ctypes.c_ulong)]
XC_FLT_TemperatureToADULin.restype = ctypes.c_ulong

# ErrCode XC_FLT_SendStream(XCHANDLE hnd, FilterID fid, XFilterMessage msg, const char * p, int len)
XC_FLT_SendStream = getattr(xenethdll, 'XC_FLT_SendStream')
XC_FLT_SendStream.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
XC_FLT_SendStream.restype = ctypes.c_ulong

# ErrCode XC_FLT_RecvStream(XCHANDLE hnd, FilterID fid, XFilterMessage msg, char * p, int * len)
XC_FLT_RecvStream = getattr(xenethdll, 'XC_FLT_RecvStream')
XC_FLT_RecvStream.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
XC_FLT_SendStream.restype = ctypes.c_ulong

# ErrCode XC_FLT_SetParameter(XCHANDLE hnd, FilterID fid, const char * parm, const char * value)
XC_FLT_SetParameter = getattr(xenethdll, 'XC_FLT_SetParameter')
XC_FLT_SetParameter.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_char_p]
XC_FLT_SetParameter.restype = ctypes.c_ulong

# ErrCode XC_FLT_GetParameter(XCHANDLE hnd, FilterID fid, const char * parm, char * value, int * len)
XC_FLT_GetParameter = getattr(xenethdll, 'XC_FLT_GetParameter')
XC_FLT_GetParameter.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
XC_FLT_GetParameter.restype = ctypes.c_ulong

# FilterID XC_AddImageFilter (XCHANDLE h, XImageFilter flt, void * parm)
XC_AddImageFilter = getattr(xenethdll, 'XC_AddImageFilter')
XC_AddImageFilter.argtypes = [ctypes.c_int, XImageFilter, ctypes.py_object]
XC_AddImageFilter.restype = ctypes.c_int

# ErrCode XC_MsgImageFilter (XCHANDLE h, FilterID fid, XFilterMessage msg, void * msgparm)
XC_MsgImageFilter = getattr(xenethdll, 'XC_MsgImageFilter')
XC_MsgImageFilter.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
XC_MsgImageFilter.restype = ctypes.c_ulong

# ErrCode XC_FLT_StreamToText(void *pStream, char *pText, int *len)
XC_FLT_StreamToText = getattr(xenethdll, 'XC_FLT_StreamToText')
XC_FLT_StreamToText.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
XC_FLT_StreamToText.restype = ctypes.c_ulong

# ErrCode XC_FLT_TextToStream(void *pStream, const char *pText, int len)
XC_FLT_TextToStream = getattr(xenethdll, 'XC_FLT_TextToStream')
XC_FLT_TextToStream.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
XC_FLT_TextToStream.restype = ctypes.c_ulong

#--------
# Footers
#--------

# dword XC_GetFrameFooterLength (XCHANDLE h)
XC_GetFrameFooterLength = getattr(xenethdll, 'XC_GetFrameFooterLength')
XC_GetFrameFooterLength.argtypes = [ctypes.c_int]
XC_GetFrameFooterLength.restype = ctypes.c_uint
