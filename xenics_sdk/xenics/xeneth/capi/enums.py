"""
Enum definitions used in the XenEth SDK
"""

# pylint: disable=C0103, disable=C0301

from enum import IntEnum, IntFlag, unique


@unique
class XEnumerationFlags(IntEnum):
    """
    Xeneth Enumeration Flags (XEF)
    Used by ao XCD_EnumerateDevices to specify the protocols to be discovered.
    Choose XEF_EnableAll to enumerate all supported protocols.
    """
    XEF_Network      = 0x00000001    # Network
    XEF_Serial       = 0x00000002    # Serial
    XEF_CameraLink   = 0x00000004    # CameraLink
    XEF_GigEVision   = 0x00000008    # GigEVision
    XEF_CoaXPress    = 0x00000010    # CoaXPress
    XEF_USB          = 0x00000020    # USB
    XEF_USB3Vision   = 0x00000040    # USB3Vision
    XEF_GenCP        = 0x00000080    # CameraLink GenCP
    XEF_EnableAll    = 0x0000FFFF    # Enable all protocols.
    XEF_UseCached    = 0x01000000    # Use cached devices on enumeration    (Not used in Python XXX)
    XEF_ReleaseCache = 0x02000000    # Release internally cached devices    (Not used in Python XXX)

@unique
class XDeviceStates(IntEnum):
    """
    Device states enumeration (XDS)
    """
    XDS_Available       = 0x0   # The device is available to establish a connection.
    XDS_Busy            = 0x1   # The device is currently in use.
    XDS_Unreachable     = 0x2   # The device was detected but is unreachable.

@unique
class XPropType(IntFlag):
    """
    Xeneth property types

    These types and their attributes are used by the property system.
    To retrieve the property type call the XCamera::GetPropertyType-method using the short name to identify the property.
    """
    XType_None           = 0x0000000
    XType_Base_Mask      = 0x000000ff    # Type mask
    XType_Attr_Mask      = 0xffffff00    # Attribute mask
    XType_Base_Number    = 0x00000001    # A number (floating)
    XType_Base_Enum      = 0x00000002    # An enumerated type (a choice)
    XType_Base_Bool      = 0x00000004    # Boolean (true / false / 1 / 0)
    XType_Base_Blob      = 0x00000008    # Binary large object
    XType_Base_String    = 0x00000010    # String
    XType_Base_Action    = 0x00000020    # Action (button)
    XType_Base_Rfu1      = 0x00000040    # RFU
    XType_Base_Rfu2      = 0x00000080    # R
    XType_Base_MinMax    = 0x00002000    # The property accepts the strings 'min' and 'max' to set the best achievable extremities.
    XType_Base_ReadOnce  = 0x00001000    # Property needs to be read at start-up only
    XType_Base_NoPersist = 0x00000800    # Property shouldn't be persisted (saved & restored)
    XType_Base_NAI       = 0x00000400    # Property does not affect image intensity level ('Not Affecting Image')
    XType_Base_RW        = 0x00000300    # Write and read back
    XType_Base_Writeable = 0x00000200    # Writeable properties have this set in their high byte
    XType_Base_Readable  = 0x00000100    # Readable properties have this set in their high by
    XType_Number         = 0x00000201    # Write only number
    XType_Enum           = 0x00000202    # Write only enumeration
    XType_Bool           = 0x00000204    # Write only boolean
    XType_Blob           = 0x00000208    # Write only binary large object
    XType_String         = 0x00000210    # Write only string
    XType_Action         = 0x00000220    # Action (button)
    XType_RO_Number      = 0x00000101    # Read only number
    XType_RO_Enum        = 0x00000102    # Read only enumeration
    XType_RO_Bool        = 0x00000104    # Read only boolean
    XType_RO_Blob        = 0x00000108    # Read only binary large object
    XType_RO_String      = 0x00000110    # Read only string
    XType_RW_Number      = 0x00000301    # R/W number
    XType_RW_Enum        = 0x00000302    # R/W enumeration
    XType_RW_Bool        = 0x00000304    # R/W boolean
    XType_RW_Blob        = 0x00000308    # R/W binary large object
    XType_RW_String      = 0x00000310    # R/W string

@unique
class XStatusMessage(IntEnum):
    """Status messages used in conjunction with the #XStatus-callback.
    """
    XSLoadLogic         = 1 # Passed when loading the camera's main logic file                           */
    XSLoadVideoLogic    = 2 # Passed when loading the camera's video output firmware                     */
    XSDataStorage       = 3 # Passed when accessing persistent data on the camera                        */
    XSCorrection        = 4 # Passed when uploading correction data to the camera                        */
    XSSelfStart         = 5 # Passed when a self starting camera is starting (instead of XSLoadLogic)    */
    XSMessage           = 6 # String event
                            # This status message is used to relay critical errors, and events originating
                            # from within the API.
                            # Cam|PropLimit|property=number - A filter notifies you your user interface should limit the value of 'property' to 'number'
                            # Cam|TemperatureFilter|RangeUpdate       - The thermography filter uses this to notify you of a span update.
                            # Cam|TemperatureFilter|Off               - The thermography filter suggests the application to dequeue the filter.
                            # Cam|InterfaceUpdate           - Internal, do not handle, returning E_BUG here causes the API to stop unpacking 'abcd.package'.packages to %appdata%/xenics/interface
    XSLoadGrabber       = 7 # Passed when loading the framegrabber                                                                                */
    XSDeviceInformation = 8 # Device information passed when connecting a device, ulP is the lower part of the address. When using 64-bit the higher part of the address is stored in ulT */

@unique
class XFrameType(IntEnum):
    """
    The supported frame types
    These are used to learn the native pixel size of the camera using XCamera::GetFrameType,
    or during frame conversions when calling the XCamera::GetFrame(FrameType, unsigned long, void *, unsigned int)-method.
    """
    FT_UNKNOWN      = -1    # Unknown invalid frame type
    FT_NATIVE       = 0     # The native frame type of this camera (can be FT_8..,FT_16..,FT32.. check GetFrameType())
    FT_8_BPP_GRAY   = 1     # 8-bit greyscale
    FT_16_BPP_GRAY  = 2     # 16-bit greyscale (default for most of the Xenics branded cameras)
    FT_32_BPP_GRAY  = 3     # 32-bit greyscale
    FT_32_BPP_RGBA  = 4     # 32-bit colour RGBA      [B,G,R,A] Available for output conversion.
    FT_32_BPP_RGB   = 5     # 32-bit colour RGB       [B,G,R]   Available for output conversion.
    FT_32_BPP_BGRA  = 6     # 32-bit colour BGRA      [R,G,B,A]
    FT_32_BPP_BGR   = 7     # 32-bit colour BGR       [R,G,B]

@unique
class XGetFrameFlags(IntFlag):
    """
    The XCamera::GetFrame(FrameType, unsigned long, void *, unsigned int)-flags
    These flags are used to control the way the GetFrame-method works.
    """
    XGF_Blocking     = 1     # In blocking-mode the method does not return immediately with the return codes #E_NO_FRAME / #I_OK.
                             # Instead the method waits for a frame and only returns until a frame was captured, or a time-out period has elapsed.
    XGF_NoConversion = 2     # Prevents internal conversion to 8 bit, specifying this flag reduces computation time, but prevents #SaveData() and the #Blit() method from working.
    XGF_FetchPFF     = 4     # Retrieve the per frame footer with frame timing information. Call XCamera::GetFrameFooterLength() to determine the increase in frame size.
    XGF_RFU_1        = 8
    XGF_RFU_2        = 16
    XGF_RFU_3        = 32

@unique
class ColourMode(IntFlag):
    """
    Defines different colour modes.
    """
    ColourMode_8            = 0     # Intensity only
    ColourMode_16           = 1     # Alias
    ColourMode_Profile      = 2     # Uses a colour profile bitmap. See #LoadColourProfile()
    ColourMode_Invert       = 256   # Set this flag if an inversion of the colour profile is desired. eg: #ColourMode_8 | #ColourMode_Invert


@unique
class XFilterMessage(IntEnum):
    """ Image filter messages """

    XMsgInit                = 0         # [API->Filter Event] Called when the filter is being installed  ( (!) calling thread context)
    XMsgClose               = 1         # [API->Filter Event] Called when the filter is being removed    ( (!) calling thread context)
    XMsgFrame               = 2         # [API->Filter Event] Called after every frame grab              ( (!) grabbing thread context)
    XMsgGetName             = 3         # [App->Filter Event] Retrieve filter name: the filter should copy a friendly string to msgparm
    XMsgGetValue            = 4         # [Obsolete]
    XMsgSave                = 5         # [Obsolete]
    XMsgGetStatus           = 6         # [API->Filter Event] Retrieves a general purpose status message from the image filter
    XMsgUpdateViewPort      = 7         # [API->Filter Event] Instructs an image correction filter to update it's view port
                                        #                     This message is sent to a filter upon changing the window of interest, or when
                                        #                     flipping image horizontally or vertically                                        */
    XMsgCanProceed          = 8         # Used by image filters in in interactive mode to indicate acceptable image conditions                 */
    XMsgGetInfo             = 9         # [Internal]          Used to query filter 'registers'                                                 */
    XMsgSelect              = 10        # [Obsolete]                                                                                           */
    XMsgProcessedFrame      = 11        # [API->Filter Event] Sent after other filters have done their processing. Do not modify the frame data
                                        #                     in response to this event.                                                       */
    XMsgTimeout             = 13        # [API->Filter Event] A camera time-out event was generated                                             */
    XMsgIsBusy              = 16        # [Thermography]      Is the temperature filter recalculating - Used to check if the thermal filter is
                                        #                     still updating it's linearisation tables                                         */
    XMsgSetTROI             = 17        # [Imaging/Thermo]    Set the adu/temperature span in percent, (see #XMsgSetTROIParms)                 */
    XMsgLoad                = 18        # [Obsolete]                                                                                           */
    XMsgUnload              = 19        # [Obsolete]                                                                                           */
    XMsgADUToTemp           = 12        # [Thermography]      Convert an ADU value to a temperature (see #XFltADUToTemperature)                 */
    XMsgGetEN               = 14        # [Obsolete]          Get temperature correction parameters (see #XMsgGetRadiometricParms)              */
    XMsgSetEN               = 15        # [Obsolete]          Set temperature correction parameters (see #XMsgGetRadiometricParms)              */
    XMsgTempToADU           = 20        # [Thermography]      Convert a temperature to an ADU value (see #XFltTemperatureToADU)                 */
    XMsgGetTValue           = 21        # [Thermography]      Retrieve an emissivity corrected value from a coordinate                         */
    XMsgGetRadiometricParms = 22        # [Thermography]      Get temperature correction parameters (see #XMsgTempParms)                        */
    XMsgSetRadiometricParms = 23        # [Thermography]      Set temperature correction parameters (see #XMsgTempParms)                        */
    XMsgSerialise           = 100       # [App->Filter event] Serialise internal parameter state (write xml structure) see #XFltSetParameter    */
    XMsgDeserialise         = 101       # [App->Filter event] Deserialise parameter state (read xml structure) see #XFltSetParameter            */
    XMsgGetPriority         = 102       # [Filter Management] Write the current filter priority to the long * provided in v_pMsgParm           */
    XMsgSetFilterState      = 104       # [Filter Management] Enable or disable an image filter temporarily by sending 0/1 in v_pMsgParm       */
    XMsgIsSerialiseDirty    = 105       # [Internal]                                                                                           */
    XMsgStoreHandle         = 106       # [Internal]          Start tracking the module handle for plugin image filters                        */
    XMsgUpdateTint          = 107       # [API->Filter event] Integration time change notification                                             */
    XMsgLinADUToTemp        = 109       # [Thermography]      Convert a Linearized ADU value to a temperature (see #XFltADUToTemperatureLin)    */
    XMsgLinTempToADU        = 110       # [Thermography]      Convert a temperature to a Linearized ADU value (see #XFltTemperatureToADULin)    */
    XMsgUpdateSpan          = 111       # [API->Filter event] Span change notification                                                         */
    XMsgUpdatePalette       = 112       # [API->Filter event] Colour profile change notification                                               */
    XMsgFilterQueued        = 113       # [API->Filter event] A filter is queued                                                               */
    XMsgFilterRemoved       = 114       # [API->Filter event] A filter is removed                                                              */
    XMsgDrawOverlay         = 200       # [API->Filter event] Draw the RGBA frame overlay, v_pMsgParm is the pointer to the RGBA data
                                        #                     structure                                                                        */
    XMsgLineariseOutput     = 201       # [Thermography]      When specifying a v_pMsgParm that is non zero, starts linearising adu output     */
    XMsgSetEmiMap           = 202       # [Thermography]      Streams the main emissivity map to the thermal filter (16 bit png, 65535 = 1.0)  */
    XMsgSetEmiMapUser       = 203       # [Thermography]      Stream a user emissivity map to the thermal filter (16 bit png, 65535 = 1.0,
                                        #                     0 values are replaced by the emissivity in the main map)                         */
    XMsgGetEmiMap           = 204       # [Thermography]      Stream out the combined emissivity map                                           */
    XMsgClrEmiMap           = 205       # [Thermography]      Clear emissivity map                                                             */
    XMsgClrEmiMapUser       = 206       # [Thermography]      Clear emissivity map (user)                                                      */
    XMsgPushRange           = 207       # [Thermography]      Push a new linearization range to the thermal filter                             */
    XMsgThmFilterState      = 208       # [Thermography]      Filter event indicating thermal filter queue/removal                             */
    XMsgThmAdjustSet        = 209       # [Thermography]      Set global offset & gain adu adjustment (pre-thermal conversion)                 */
    XMsgThmAdjustGet        = 210       # [Thermography]      (see #XMsgTempAdjustmentParms)                                                      */

    XMsgLog                 = 211       # [Plugin->API]       Fire a log event to the end user application\n
                                        #                     Target filter id: 0xffffffff                                                */
    XMsgGetDeltaT           = 212       # [Internal]                                                                                      */
    XMsgGetTintRange        = 213       # [Plugin->API]       Request the exposure time range
                                        #                     Target filter id: 0xffffffff                                                 */
    XMsgCorrectionDirty         = 214   # [Internal]          The onboard thermography parameters have changed                             */
    XMsgHasRadianceInfo         = 215   # [Thermography]      Check if the radiance information is available. This is needed to for emissivity correction */
    XMsgCorrectionDataChanged   = 216   # [Internal]          New correction data is loaded                             */
    XMsgPostProcess             = 217   # [Internal]          A post processing step is introduced in the software correction filter */

    XMsgZoomLensConnect     = 300       #  [Zoom lens]         Connect to the zoom lens on the specified port.  */
    XMsgZoomLensGetState    = 301       #  [Zoom lens]         Get the current zoom/focus state from the zoom lens filter.  */
    XMsgZoomLensSetState    = 302       #  [Zoom lens]         Set the current zoom/focus state in the zoom lens filter.    */
    XMsgZoomLensGetInfo     = 303       #  [Zoom lens]         Get some descriptive information about the connected lens.   */

    XMsgUser                = 24200     # If you develop your own image filter plugins, please use this constant to offset your messages. */

@unique
class XLoadCalibrationFlags(IntFlag):
    """
    Flags for the XC_LoadCalibration function
    """
    XLC_StartSoftwareCorrection = 1
    XLC_RFU_1 = 2
    XLC_RFU_2 = 4
    XLC_RFU_3 = 8

@unique
class XSaveDataFlags(IntFlag):
    """
    Flags for XCamera's SaveData method
    """
    XSD_Force16 = 1          # Forces 16-bit output independent of the current ColourMode-setting (only possible for PNG's)
    XSD_Force8 = 2           # Forces 8-bit output independent of the current ColourMode
    XSD_AlignLeft = 4        # Left aligns 16-bit output (XSD_Force16 | XSD_AlignLeft)
    XSD_SaveThermalInfo = 8  # Save thermal conversion structure (only available when saving 16-bit PNGs)
    XSD_RFU_0 = 16           # Reserved
    XSD_RFU_1 = 32           # Reserved
    XSD_RFU_2 = 64           # Reserved
    XSD_RFU_3 = 128          # Reserved

@unique
class BlitType(IntEnum):
    """The different destinations supported by the XC_Blit function"""

    Window = 0  # Blit the contents of the last captured frame directly to a Windows client device context using a Window handle (HWND)
    DeviceContext = 1  # Blit the contents of the last captured frame to a specified device context. This can be any device context (HDC) like a memory DC, paint DC or a handle to a DC associated with a Graphics-object (C#)

@unique
class XDirectories(IntEnum):
    """
    Enum representing Xeneth directory identifiers.
    """
    XDir_FilterData = 0      # Filter data (%APPDATA%/XenICs/Data/<sessionnumber>)
    XDir_ScriptRoot = 1      # Script root (%APPDATA%/XenICs/Interface/<PID-number>)
    XDir_Calibrations = 2    # Calibration folder (%ProgramFiles%/Xeneth/Calibrations)
    XDir_InstallDir = 3      # Installation folder (%CommonProgramFiles%/XenICs/Runtime)
    XDir_Plugins = 4         # Plugin folder (%CommonProgramFiles%/XenICs/Runtime/Plugins)
    XDir_CachePath = 5       # Cache folder (%APPDATA%/XenICs/Cache)
    XDir_SdkResources = 6    # SDK resource folder (%CommonProgramFiles%/XenICs/Runtime/Resources)
    XDir_Xeneth = 7          # Xeneth installation directory
    XDir_GrabberScriptRoot = 8  # Script root (%APPDATA%/XenICs/Interface/<FrameGrabber>)
