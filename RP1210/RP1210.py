"""
Base RP1210 functions.
"""
import os
import configparser
from configparser import ConfigParser
from ctypes import POINTER, c_char_p, c_int32, c_long, c_short, c_void_p, cdll, CDLL, create_string_buffer
from typing import Literal
from RP1210 import Commands, sanitize_msg_param

RP1210_ERRORS = {
    1: "NO_ERRORS",
    128: "ERR_DLL_NOT_INITIALIZED",
    129: "ERR_INVALID_CLIENT_ID",
    130: "ERR_CLIENT_ALREADY_CONNECTED",
    131: "ERR_CLIENT_AREA_FULL",
    132: "ERR_FREE_MEMORY",
    133: "ERR_NOT_ENOUGH_MEMORY",
    134: "ERR_INVALID_DEVICE",
    135: "ERR_DEVICE_IN_USE",
    136: "ERR_INVALID_PROTOCOL",
    137: "ERR_TX_QUEUE_FULL",
    138: "ERR_TX_QUEUE_CORRUPT",
    139: "ERR_RX_QUEUE_FULL",
    140: "ERR_RX_QUEUE_CORRUPT",
    141: "ERR_MESSAGE_TOO_LONG",
    142: "ERR_HARDWARE_NOT_RESPONDING",
    143: "ERR_COMMAND_NOT_SUPPORTED",
    144: "ERR_INVALID_COMMAND",
    145: "ERR_TXMESSAGE_STATUS",
    146: "ERR_ADDRESS_CLAIM_FAILED",
    147: "ERR_CANNOT_SET_PRIORITY",
    148: "ERR_CLIENT_DISCONNECTED",
    149: "ERR_CONNECT_NOT_ALLOWED",
    150: "ERR_CHANGE_MODE_FAILED",
    151: "ERR_BUS_OFF",
    152: "ERR_COULD_NOT_TX_ADDRESS_CLAIMED",
    153: "ERR_ADDRESS_LOST",
    154: "ERR_CODE_NOT_FOUND",
    155: "ERR_BLOCK_NOT_ALLOWED",
    156: "ERR_MULTIPLE_CLIENTS_CONNECTED",
    157: "ERR_ADDRESS_NEVER_CLAIMED",
    158: "ERR_WINDOW_HANDLE_REQUIRED",
    159: "ERR_MESSAGE_NOT_SENT",
    160: "ERR_MAX_NOTIFY_EXCEEDED",
    161: "ERR_MAX_FILTERS_EXCEEDED",
    162: "ERR_HARDWARE_STATUS_CHANGE",
    202: "ERR_INI_FILE_NOT_IN_WIN_DIR",
    204: "ERR_INI_SECTION_NOT_FOUND",
    205: "ERR_INI_KEY_NOT_FOUND",
    206: "ERR_INVALID_KEY_STRING",
    207: "ERR_DEVICE_NOT_SUPPORTED",
    208: "ERR_INVALID_PORT_PARAM",
    213: "ERR_COMMAND_TIMED_OUT",
    220: "ERR_OS_NOT_SUPPORTED",
    222: "ERR_COMMAND_QUEUE_IS_FULL",
    224: "ERR_CANNOT_SET_CAN_BAUDRATE",
    225: "ERR_CANNOT_CLAIM_BROADCAST_ADDRESS",
    226: "ERR_OUT_OF_ADDRESS_RESOURCES",
    227: "ERR_ADDRESS_RELEASE_FAILED",
    230: "ERR_COMM_DEVICE_IN_USE",
    275: "ERR_OPENING_PORT", # Nexiq-specific
    441: "ERR_DATA_LINK_CONFLICT",
    453: "ERR_ADAPTER_NOT_RESPONDING",
    454: "ERR_CAN_BAUD_SET_NONSTANDARD",
    455: "ERR_MULTIPLE_CONNECTIONS_NOT_ALLOWED_NOW",
    456: "ERR_J1708_BAUD_SET_NONSTANDARD",
    457: "ERR_J1939_BAUD_SET_NONSTANDARD",
    458: "ERR_IS015765_BAUD_SET_NONSTANDARD",
    600: "ERR_INVALID_IOCTL_ID",
    601: "ERR_NULL_PARAMETER",
    602: "ERR_HARDWARE_NOT_SUPPORTED",
    603: "ERR_CANNOT_DETERMINE_BAUD_RATE"}
"""RP1210 error codes. Use this to translate ClientConnect output and other error codes."""

RP1210_COMMANDS = {
    0 : "Reset_Device",
    3 : "Set_All_Filters_States_to_Pass",
    4 : "Set_Message_Filtering_For_J1939",
    5 : "Set_Message_Filtering_For_CAN",
    7 : "Set_Message_Filtering_For_J1708",
    8 : "Set_Message_Filtering_For_J1850",
    9 : "Set_Message_Filtering_For_ISO15765",
    14 : "Generic_Driver_Command",
    15 : "Set_J1708_Mode",
    16 : "Echo_Transmitted_Messages",
    17 : "Set_All_Filters_States_to_Discard",
    18 : "Set_Message_Receive",
    19 : "Protect_J1939_Address",
    20 : "Set_Broadcast_For_J1708",
    21 : "Set_Broadcast_For_CAN",
    22 : "Set_Broadcast_For_J1939",
    23 : "Set_Broadcast_For_J1850",
    24 : "Set_J1708_Filter_Type",
    25 : "Set_J1939_Filter_Type",
    26 : "Set_CAN_Filter_Type",
    27 : "Set_J1939_Interpacket_Time",
    28 : "SetMaxErrorMsgSize",
    29 : "Disallow_Further_Connections",
    30 : "Set_J1850_Filter_Type",
    31 : "Release_J1939_Address",
    32 : "Set_ISO15765_Filter_Type",
    33 : "Set_Broadcast_For_ISO15765",
    34 : "Set_ISO15765_Flow_Control",
    35 : "Clear_ISO15765_Flow_Control",
    37 : "Set_J1939_Baud",
    38 : "Set_ISO15765_Baud",
    215 : "Set_BlockTimeout",
    305 : "Set_J1708_Baud",
    39 : "Flush_Tx_Rx_Buffers",
    41 : "Set_Broadcast_For_KWP2000",
    42 : "Set_Broadcast_For_ISO9141",
    45 : "Get_Protocol_Connection_Speed",
    46 : "Set_ISO9141KWP2000_Mode",
    47 : "Set_CAN_Baud",
    48 : "Get_Wireless_State"}
"""Mnemonics for RP1210_SendCommand commands. Follows ordering of table in section 21.4."""

IOCTL_IDS = {
    0x01 : "GET_CONFIG",
    0x02 : "SET_CONFIG",
    0x04 : "FIVE_BAUD_INIT",
    0x05 : "FAST_INIT",
    0x06 : "ISO9141_K_LINE_ONLY"
    #0x03, 0x07 - 0xFFFF    reserved for TMC
    #0x10000 - OxFFFFFFFF   vendor specific
}
"""IOCTL ID values - use these to lookup inputs to Ioctl function."""

def translateErrorCode(ClientID :int) -> str:
        """
        Matches clientID with error string in RP1210_ERRORS.

        NO_ERRORS has been expanded to cover clientID = 0 to 127.
        
        If there is no match, returns the clientID as str.
        """
        if isinstance(ClientID, str): # if this got passed a string, return the string
            return ClientID
        if ClientID < 0: # some functions return negative value for error code
            ClientID *= -1
        ClientID &= 0xFFFF # Noregon can add garbage to leading bytes
        if ClientID > 0x8000:
            ClientID = 0xFFFF - ClientID
        if 0 <= ClientID < 128:
            return "NO_ERRORS"
        return RP1210_ERRORS.get(ClientID, str(ClientID))

def getAPINames(rp121032_path : str = None) -> list[str]:
    """
    A function for reading API names from RP121032.ini. Returns a list of strings.

    Just call getAPINames() to get the API names. Then you can initialize
    an RP1210Config object using one of the API names.

    You can provide your own path to RP121032.ini, or let it find it on its own.

    Returns empty list [] if RP121032.ini isn't found or couldn't be parsed.
    """
    if not rp121032_path: # find our own path if none is given
        rp121032_path = os.path.join(os.environ["WINDIR"], "RP121032.ini")
    elif not os.path.isfile(rp121032_path): # check if file exists
        raise FileNotFoundError(f"RP121032.ini not found at {rp121032_path}.")
    try:
        parser = ConfigParser()
        parser.read(rp121032_path)
        return parser.get("RP1210Support", "APIImplementations").split(",")
    except Exception:
        return []

class RP1210Protocol:
    """
    Stores information for an RP1210 protocol, e.g. info stored in ProtocolInformationXXX sections.

    Use str() to get a pre-made string to put in a Protocol dropdown menu or info section.

    - getDescription() (str)
    - getSpeed() (list[str]) - stored as strings because it can contain "Auto"
    - getString() (str)
    - getParams() (str)
    - getDevices() (list[int])
    """
    def __init__(self,  section : dict) -> None:
        self.contents = section

    def __str__(self) -> str:
        """Returns a string that can be used in a protocol selection combo box."""
        return self.getString() + " - " + self.getDescription()

    def getDescription(self) -> str:
        """Returns ProtocolDescription parameter."""
        try:
            return self.contents["ProtocolDescription"]
        except Exception:
            return ""

    def getSpeed(self) -> list[str]:
        """Returns ProtocolSpeed parameters as a list of strings."""
        try:
            return str(self.contents["ProtocolSpeed"]).split(',')
        except Exception:
            return []

    def getString(self) -> str:
        """Returns ProtocolString parameter."""
        try:
            return self.contents["ProtocolString"]
        except Exception:
            return ""

    def getParams(self) -> str:
        """Returns ProtocolParams parameter."""
        try:
            return self.contents["ProtocolParams"]
        except Exception:
            return ""

    def getDevices(self) -> list[int]:
        """Returns a list of device IDs supported by this protocol."""
        try:
            devices = []
            section_list = str(self.contents["Devices"]).split(',')
            for device in section_list:
                devices.append(int(device))
            return devices
        except Exception:
            return []

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, RP1210Protocol):
            raise TypeError("Tried to compare RP1210Protocol with innappropriate object type.")
        return self.contents == __o.contents

    def __bool__(self):
        return bool(self.contents)

class RP1210Device:
    """
    Stores information for an RP1210 device, e.g. info stored in DeviceInformationXXX sections.

    Use str() to get a pre-made string to put in Device dropdown menu.

    - getID() (int)
    - getDescription() (str)
    - geteName() (str)
    - getParams() (str)
    - getMultiCANChannels() (int)
    - getMultiJ1939Channels() (int)
    """
    def __init__(self,  section : dict) -> None:
        self.contents = section

    def getID(self) -> int:
        """
        Returns DeviceID parameter as int.
        
        Returns -1 if DeviceID is invalid.
        """
        try:
            return int(self.contents["DeviceID"])
        except Exception:
            return -1

    def getDescription(self) -> str:
        """Returns DeviceDescription parameter."""
        try:
            return self.contents["DeviceDescription"]
        except Exception:
            return ""

    def getName(self) -> str:
        """Returns DeviceName parameter."""
        try:
            return self.contents["DeviceName"]
        except Exception:
            return ""

    def getParams(self) -> str:
        """Returns DeviceParams parameter as a string."""
        try:
            return self.contents["DeviceParams"]
        except Exception:
            return ""
    
    def getMultiCANChannels(self) -> int:
        """Returns MultiCANChannels parameter as int."""
        try:
            return int(self.contents["MultiCANChannels"])
        except Exception:
            return 0

    def getMultiJ1939Channels(self) -> int:
        """Returns MultiJ1939Channels parameter as int."""
        try:
            return int(self.contents["MultiJ1939Channels"])
        except Exception:
            return 0

    def __str__(self):
        """Returns a string that can be used in a device selection combo box."""
        ret_str = ""
        if self.getID() == -1:
            ret_str += "(Invalid Device)"
        else:
            ret_str += str(self.getID())
        if self.getDescription() != "":
            ret_str += " - " + self.getDescription()
        return ret_str

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, RP1210Device):
            raise TypeError("Tried to compare RP1210Device with innappropriate object type.")
        return self.contents == __o.contents

    def __bool__(self):
        return bool(self.contents)
         
class RP1210Config(ConfigParser):
    """
    Reads & stores Vendor API information. Child of ConfigParser. Use getAPINames() to get an
    RP1210 API name to feed to this class.

    This class has functions for reading EVERY SINGLE data field defined in the RP1210C standard.
    As such, it is embarrassingly long.

    This class holds an instance of RP1210API, which you can use to call RP1210 functions.
    - `nexiq = RP1210Config("NULN2R32")`
    - `clientID = nexiq.api.ClientConnect(args)`

    You can use str(this_object) to generate a string to display in your Vendors dropdown.
    """
    def __init__(self, api_name : str, api_path : str = None, config_path : str = None) -> None:
        super().__init__()
        self._api_name = api_name
        self._api_valid = True
        self.api = RP1210API(api_name, api_path)
        self._configDir = config_path
        self.populate()

    def __str__(self) -> str:
        """
        Returns a string that you'd typically put in a vendor selection box.
        
        Format: "api_name - adapter_description"

        Appends " - (drivers invalid)" if drivers failed to load.
        """
        if self._api_valid:
            err_str = ""
        else:
            err_str = " - (drivers invalid)"
        return self.getAPIName() + " - " + self.getName() + err_str

    def __bool__(self) -> bool:
        return self.isValid()

    def getAPI(self):
        """
        Returns RP1210API object that can be used to call RP1210 functions.

        You can also just access the api object directly.
        """
        return self.api

    def isValid(self) -> bool:
        """
        Returns self.api_valid, which is set to False if config file can't be parsed or doesn't
        include VendorInformation.

        This is a very basic check - a return value of True does not absolutely guarantee
        that the driver config file is valid and correct!
        """
        return self._api_valid

    def getAPIName(self) -> str:
        """Returns API name (i.e. the name of the .ini and .dll files)"""
        return self._api_name

    def getName(self) -> str:
        """
        Returns 'Name' field from VendorInformation section.

        Will return "(Vendor Name Missing)" if the 'Name' field isn't found.
        """
        return self.get("VendorInformation", "Name", fallback="(Vendor Name Missing)")

    def getDescription(self) -> str:
        """
        Returns 'Name' field from VendorInformation section.

        Will return "(Vendor Name Missing)" if the 'Name' field isn't found.

        This is a copy of getName(), since I personally think the name section is more like a
        description.
        """
        return self.getName()

    def getAddress1(self) -> str:
        """
        Returns 'Address1' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        return self.get("VendorInformation", "Address1", fallback="")

    def getAddress2(self) -> str:
        """
        Returns 'Address2' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        return self.get("VendorInformation", "Address2", fallback="")

    def getCity(self) -> str:
        """
        Returns 'City' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        return self.get("VendorInformation", "City", fallback="")

    def getState(self) -> str:
        """
        Returns 'State' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        return self.get("VendorInformation", "State", fallback="")

    def getCountry(self) -> str:
        """
        Returns 'Country' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        return self.get("VendorInformation", "Country", fallback="")

    def getPostal(self) -> str:
        """
        Returns 'Postal' field (zipcode) from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        return self.get("VendorInformation", "Postal", fallback="")

    def getTelephone(self) -> str:
        """
        Returns 'Telephone' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        return self.get("VendorInformation", "Telephone", fallback="")

    def getFax(self) -> str:
        """
        Returns 'Fax' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        return self.get("VendorInformation", "Fax", fallback="")

    def getVendorURL(self) -> str:
        """
        Returns the VendorURL field in VendorInformation section.
        
        Returns empty string if VendorURL field isn't found.
        """
        return self.get("VendorInformation", "VendorURL", fallback="")

    def getVersion(self) -> str:
        """
        Returns the 'Version' field from VendorInformation section.
        
        Returns empty string if Version field isn't found.
        """
        return self.get("VendorInformation", "Version", fallback="")

    def getAutoDetectCapable(self) -> bool:
        """
        Returns the 'AutoDetectCapable' field from VendorInformation section.

        Returns False if the field isn't found.
        """
        try:
            return self.getboolean("VendorInformation", "AutoDetectCapable", fallback=False)
        except (ValueError, KeyError):
            return False

    def autoDetectCapable(self) -> bool:
        """
        Returns the 'AutoDetectCapable' field from VendorInformation section.

        Returns False if the field isn't found.

        This function is a duplicate of getAutoDetectCapable().
        """
        return self.getAutoDetectCapable()

    def getTimeStampWeight(self) -> float:
        """
        Returns the 'TimeStampWeight' field in VendorInformation section.

        Returns 1.0 if the field isn't found.
        """
        try:
            return self.getfloat("VendorInformation", "TimeStampWeight", fallback=1.0)
        except (ValueError, KeyError):
            return 1.0

    def getMessageString(self) -> str:
        """
        Returns the 'MessageString' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        return self.get("VendorInformation", "MessageString", fallback="")

    def getErrorString(self) -> str:
        """
        Returns the 'ErrorString' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        return self.get("VendorInformation", "ErrorString", fallback="")

    def getRP1210Version(self) -> str:
        """
        Returns the 'RP1210' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        return self.get("VendorInformation", "RP1210", fallback="")

    def getDebugLevel(self) -> int:
        """
        Returns the 'DebugLevel' field in VendorInformation section.
        - -1 = Debugging is not supported by this API.
        - 0 = No debugging to be accomplished.
        - 1 = Only Connect/Disconnect/Error Messages.
        - 2 = Add RP1210 SendCommand calls.
        - 3 = Add all sent Messages (with filtering).
        - 4 = Add all Received Messages (with filtering).

        Returns -1 (debugging not supported) if the field isn't found.
        """
        try:
            return self.getint("VendorInformation", "DebugLevel", fallback=-1)
        except (ValueError, KeyError):
            return -1

    def getDebugFile(self) -> str:
        """
        Returns the 'DebugFile' field in VendorInformation section.

        This represents the absolute path to the debug/log file.

        Returns a blank string if the field isn't found.
        """
        return self.get("VendorInformation", "DebugFile", fallback="")

    def getDebugMode(self) -> int:
        """
        Returns the 'DebugMode' field in VendorInformation section.
        - 0 = Overwrite (completely destroying previous contents) 
        - 1 = Append (write to the end of the file, keeping any previous contents) 

        Returns -1 if the field isn't found.
        """
        try:
            return self.getint("VendorInformation", "DebugMode", fallback=-1)
        except (ValueError, KeyError):
            return -1

    def getDebugFileSize(self) -> int:
        """
        Returns the 'DebugFileSize' field in VendorInformation section.
        
        This represents the maximum size in kilobytes that the debug file should be.
        If this field is missing (and debug logging is enabled), it defaults to 1024 KB (1MB).

        Returns 1024 (default size) if the field isn't found. Please note that if DebugLevel = -1,
        there will be no logging even if you receive a value of 1024 from this function.
        """
        try:
            return self.getint("VendorInformation", "DebugFileSize", fallback=1024)
        except (ValueError, KeyError):
            return 1024

    def getNumberOfSessions(self) -> int:
        """
        Returns the 'NumberOfRTSCTSSessions' field in VendorInformation section.

        'NumberOfRTSCTSSessions' is an integer representing the number of concurrent RTS/CTS
        transport sessions that the API supports per client.

        Returns 1 (default value) if the field isn't found.
        """
        try:
            return self.getint("VendorInformation", "NumberOfRTSCTSSessions", fallback=1)
        except (ValueError, KeyError):
            return 1

    def getCANFormatsSupported(self) -> list[int]:
        """
        Returns the 'CANFormatsSupported' list in VendorInformation section.

        These numbers correspond with the CAN Formats described in section 12.8 of the RP1210C 
        documentation.

        Returns an empty list if the field isn't found.
        """
        if not self.has_option("VendorInformation", "CANFormatsSupported"):
            return []
        try:
            return [int(i) for i in self["VendorInformation"]["CANFormatsSupported"].split(",")]
        except Exception:
            return []

    def getJ1939FormatsSupported(self) -> list[int]:
        """
        Returns the 'J1939FormatsSupported' list in VendorInformation section.

        These numbers correspond with the J1939 Formats described in section 12 of the RP1210C 
        documentation.

        Returns an empty list if the field isn't found.
        """
        if not self.has_option("VendorInformation", "J1939FormatsSupported"):
            return []
        try:
            params = []
            for param in self["VendorInformation"]["J1939FormatsSupported"].split(","):
                params.append(int(param))
            return params
        except Exception:
            return []

    def getCANAutoBaud(self) -> bool:
        """Returns the CANAutoBaud field in VendorInformation."""
        try:
            return self.getboolean("VendorInformation", "CANAutoBaud", fallback=False)
        except (ValueError, KeyError):
            return False

    def autoBaudEnabled(self) -> bool:
        """
        Returns the CANAutoBaud field in VendorInformation.
        
        Duplicate of CANAutoBaud() function.
        """
        return self.getCANAutoBaud()

    def getDevice(self, deviceID : int) -> RP1210Device:
        """
        Returns RP1210Device object matching deviceID.
        
        Returns None if the Device isn't found.
        """
        try:
            return RP1210Device(self["DeviceInformation" + str(deviceID)])
        except Exception:
            return None

    def getDevices(self) -> list[RP1210Device]:
        """
        Returns a list of RP1210Device objects read from this file.
        """
        try:
            deviceList = [] #type: list[RP1210Device]
            deviceIDs = self.getDeviceIDs()
            for device_num in deviceIDs:
                section = self["DeviceInformation" + str(device_num)]
                deviceList.append(RP1210Device(section))
            return deviceList
        except Exception:
            return []

    def getDeviceIDs(self) -> list[int]:
        """Returns list of DeviceIDs described in .ini file."""
        try:
            devices = []
            for device in self["VendorInformation"]["Devices"].split(","):
                devices.append(int(device))
            return devices
        except Exception:
            return []

    def getProtocol(self, protocol = "J1939") -> RP1210Protocol:
        """
        Returns RP1210Protocol object matching protocol arg.

        protocol can be a string or an int.

        Returns None if the protocol isn't found.
        """
        try:
            if isinstance(protocol, int):
                section = self["ProtocolInformation" + str(protocol)]
                return RP1210Protocol(section)
            elif isinstance(protocol, str):
                for pid in self.getProtocolIDs():
                    p = self.getProtocol(pid)
                    if p.getString() == protocol:
                        return p
            return None
        except Exception:
            return None
    
    def getProtocols(self) -> list[RP1210Protocol]:
        """
        Returns a list of RP1210Protocol objects generated from .ini file.
        
        Returns an empty list if protocol objects couldn't be generated.
        """
        try:
            names = self.getProtocolNames()
            protocols = [] # type: list[RP1210Protocol]
            for name in names:
                protocols.append(self.getProtocol(name))
            return protocols
        except Exception:
            return []

    def getProtocolNames(self) -> list[str]:
        """
        Returns a list of protocol Strings.

        Returns [] if no protocols are found.
        """
        try:
            protocol_ids = self.getProtocolIDs()
            if not protocol_ids:
                return []
            strings = []
            for protocol_num in protocol_ids:
                strings.append(self.getProtocol(protocol_num).getString())
            return strings
        except Exception:
            return []

    def getProtocolIDs(self) -> list[int]:
        """Returns list of ProtocolIDs described in .ini file."""
        try:
            if not self.has_option("VendorInformation", "Protocols"):
                return []
            return [int(i) for i in self["VendorInformation"]["Protocols"].split(",")]
        except Exception:
            return []

    def populate(self):
        """Reads .ini file for the specified RP1210 API."""
        
        try:
            path = self.getPath()
            if not os.path.exists(path):
                raise IOError
            self.read(path)
            if not self.has_section("VendorInformation"):
                self._api_valid = False
        except (configparser.Error, IOError):
            self._api_valid = False

    def getPath(self) -> str:
        """Returns absolute path to API config file."""
       
        if self._configDir is not None:
            if os.path.abspath(self._configDir):

                if os.path.isfile(self._configDir):
                    # [provided absolute path]
                    return self._configDir
                else:
                    # [provided absolute dir] + [api name].ini
                    return os.path.join(self._configDir, self._api_name + ".ini")

            else:
                if os.path.isfile(os.path.join(os.curdir, self._configDir)):
                    # [current directory] + [provided relative path]
                    return os.path.join(os.curdir, self._configDir)
                else:
                    return os.path.join(os.curdir, self._configDir + self._api_name + ".ini")
                    # [current directory] + [provided relative dir] + [api name].ini
                
        else:
            return os.path.join(os.environ["WINDIR"], self._api_name + ".ini")

class RP1210API:
    """
    Interface with RP1210 API to call functions from your adapter's drivers.

    See function docstrings for details on each function.
    """
    def __init__(self, api_name : str, WorkingAPIDirectory : str = None) -> None:
        self._api_valid = False
        self._api_name = api_name
        self.dll = None
        self._conforms_to_rp1210c = True
        self._libDir = WorkingAPIDirectory

    def __bool__(self):
        return self.isValid()

    def __str__(self):
        return self._api_name

    def getAPIName(self) -> str:
        """Returns API name for this API."""
        return self._api_name

    def getDLL(self) -> CDLL:
        """
        Returns CDLL object for this RP1210 API.

        Will return None if cdll.LoadLibrary was unsuccessful.
        """
        if not self.dll:
            self.loadDLL()
        return self.dll

    def loadDLL(self) -> CDLL:
        """
        Loads and returns CDLL for this API.
        
        If you already called `loadDLL()`, you can call `getDLL()` to get the DLL you loaded previously.

        Can take in a relative and absolute paths files and directories.
        
        If given a directory (by setting `WorkingAPIDirectory` param in `__init__()`), will attempt to
        load DLL corresponding to `self._api_name` from that directory. If a working directory is not provided at
        initialization of `RP1210API()`, will assume relative to launch path.
        """
        if self._libDir is not None:
            path = ""
            if not os.path.isabs(self._libDir):
                # If path given is relative, get the working directory
                if self._libDir is not None:
                    path += self._libDir
                else:
                    path += os.path.abspath(os.curdir)

            path += self._libDir
                
            if not os.path.isfile(path):
                # Append API name to complete path
                path += self._api_name + ".dll"
            try:
                dll = cdll.LoadLibrary(path)
                self.setDLL(dll)
                return dll
            except Exception: # Couldn't load from input
                self._api_valid = False
                return None
        else:
            try:
                try:
                    path = self._api_name + ".dll"
                    dll = cdll.LoadLibrary(path)
                except OSError:
                    # Try "DLL installed in wrong directory" band-aid
                    path = self._get_alternate_dll_path()
                    dll = cdll.LoadLibrary(path)
                self.setDLL(dll)
                return dll
            except Exception: # RIP
                self._api_valid = False
                return None

    def isValid(self) -> bool:
        """
        Returns api_valid boolean, which is set when the DLL is loaded.

        This function will load the DLL if it wasn't loaded already.
        
        True = DLL loaded, False = DLL failed to load
        """
        self.getDLL()
        return self._api_valid

    def conformsToRP1210C(self) -> bool:
        """
        Returns True if the drivers appear to conform to the RP1210C standard, False if not.

        This function will load the DLL if it wasn't loaded already.
        
        You can do this more easily by reading the RP1210 Version field in RP1210Interface.
        """
        if not self.isValid():
            return False
        return self._conforms_to_rp1210c

    def setDLL(self, dll : CDLL):
        """Sets the CDLL used to call RP1210 API functions."""
        try:
            self.dll = dll
            if self.dll: # check it's not None
                self._init_functions()
                self._api_valid = True
            else:
                self._api_valid = False
        except OSError:
            self._api_valid = False

    def ClientConnect(self, DeviceID : int, Protocol = b"J1939:Baud=Auto", TxBufferSize = 8000, 
                            RcvBufferSize = 8000, isAppPacketizingincomingMsgs = 0) -> int:
        """
        Attempts to connect to an RP1210 adapter.
        - DeviceID determines which adapter it tries to connect to.
        - You can generate Protocol with a protocol format function, e.g. getJ1939ProtocolString(),
        or just do it yourself.
            - Protocol defaults to b"J1939:Baud=Auto"
        - Tx and Rcv buffer sizes default to 8K.
        - Don't mess with argument nisAppPacketizingincomingMsgs.

        Returns ClientID. 0 to 127 means connection was successful; >127 means it failed.

        Use function translateClientID() to translate ClientID into an error message.
        """
        clientID = self.getDLL().RP1210_ClientConnect(0, DeviceID, sanitize_msg_param(Protocol),
                                        TxBufferSize, RcvBufferSize, isAppPacketizingincomingMsgs)
        return self._validate_and_fix_clientid(clientID)
    
    def ClientDisconnect(self, ClientID : int) -> int:
        """
        Disconnects client w/ specified ClientID from adapter.
        
        Returns 0 if successful, or >127 if it failed.
            You can use translateClientID() to translate the failure code.
        """
        return self.getDLL().RP1210_ClientDisconnect(ClientID) & 0xFFFF

    def SendMessage(self, ClientID : int, ClientMessage : bytes, MessageSize = 0) -> int:
        """
        Send a message to the databus your adapter is connected to.
        - ClientID = clientID you got from ClientConnect
        - ClientMessage = message you want to send
        - MessageSize = message size in bytes (including qualifier bytes like timestamp)
            - Will default to len(ClientMessage) if MessageSize = 0
        
        Use a Message class provided with this package (e.g. J1939Message) to generate the
        message. Or just do it yourself, I'm not the boss of you.

        Returns 0 if successful, or >127 if it failed.
            You can use translateClientID() to translate the failure code.
        """
        msg = sanitize_msg_param(ClientMessage)
        if MessageSize == 0:
            MessageSize = len(msg)
        ret_val = self.getDLL().RP1210_SendMessage(ClientID, msg, MessageSize, 0, 0) & 0xFFFF
        # check for error codes. ret_val is a 16-bit unsigned int, so must be converted
        # to negative signed int.
        if ret_val >= 0x08000:
            ret_val = (ret_val - 0x10000)
        return ret_val

    def ReadMessage(self, ClientID : int, RxBuffer : bytes, BufferSize = 0, 
                        BlockOnRead = 0) -> int:
        """
        Rx function.
        - ClientID = clientID you got from ClientConnect
        - RxBuffer = buffer you want to read the message into (called fpchAPIMessage in RP1210 docs)
            - Generate this via create_string_buffer()
        - BufferSize = the size of the buffer in bytes. Defaults to len(RxBuffer) if no value
        is provided.
        - BlockOnRead = sets NON_BLOCKING_IO or BLOCKING_IO. Defaults to NON_BLOCKING_IO.
        
        Returns the number of bytes read (including 4 bytes for timestamp). Returns 0 if no message
        is present. Returns a negative number containing an error code if there was an error, e.g.
        -128 -> error code 128.
        """
        if not BufferSize:
            BufferSize = len(RxBuffer)
        ret_val = self.getDLL().RP1210_ReadMessage(ClientID, RxBuffer, BufferSize, BlockOnRead) & 0xFFFF
        # check for error codes. ret_val is a 16-bit unsigned int, so must be converted
        # to negative signed int.
        if ret_val >= 0x8000:
            ret_val = (ret_val - 0x10000)
        return ret_val

    def ReadDirect(self, ClientID : int, BufferSize = 256, BlockOnRead = 0) -> bytes:
        """
        Calls ReadMessage, but generates and returns its own RxBuffer as bytes.
        - ClientID = clientID you got from ClientConnect
        - BufferSize = the size of the buffer in bytes. Defaults to 256.
        - BlockOnRead = sets NON_BLOCKING_IO or BLOCKING_IO. Defaults to NON_BLOCKING_IO.

        Output still includes leading 4 timestamp bytes, if applicable.
        """
        RxBuffer = create_string_buffer(BufferSize)
        size = self.ReadMessage(ClientID, RxBuffer, BufferSize, BlockOnRead)
        if size <= 0:
            return b''
        return RxBuffer[:size]

    def ReadVersion(self, DLLMajorVersionBuffer : bytes, 
                        DLLMinorVersionBuffer : bytes,
                        APIMajorVersionBuffer : bytes,
                        APIMinorVersionBuffer : bytes) -> None:
        """
        RP1210_ReadVersion function in all its glory. Provide it with four buffers via
        create_string_buffer(16). This function will overwrite each buffer with whatever it reads
        from the DLL.

        Usage of ReadVersionDirect() instead of this function is highly recommended.
        """
        return self.getDLL().RP1210_ReadVersion(DLLMajorVersionBuffer, DLLMinorVersionBuffer, 
                                                APIMajorVersionBuffer, APIMinorVersionBuffer) & 0xFFFF

    def ReadVersionDirect(self, BufferSize = 16) -> tuple:
        """
        Reads API and DLL version info. Returns a tuple containing (in order):
        - DLLVersion (str) - major.minor, e.g. "3.1"
        - APIVersion (str) - major.minor, e.g. "3.1"

        Arg BufferSize can be used to specify the size of the buffers used to read each element.

        This function checks your RP1210 drivers; there is no communication with an adapter.
        """
        DLLMajorVersion = create_string_buffer(BufferSize)
        DLLMinorVersion = create_string_buffer(BufferSize)
        APIMajorVersion = create_string_buffer(BufferSize)
        APIMinorVersion = create_string_buffer(BufferSize)
        self.getDLL().RP1210_ReadVersion(DLLMajorVersion, DLLMinorVersion, 
                                        APIMajorVersion, APIMinorVersion)
        dll_version = str(DLLMajorVersion.value + b"." + DLLMinorVersion.value, "utf-8")
        api_version = str(APIMajorVersion.value + b"." + APIMinorVersion.value, "utf-8")
        return (dll_version, api_version)

    def ReadDLLVersion(self) -> str:
        """
        Reads DLL version from adapter drivers.

        All this function does is call ReadVersionDirect() and return its first element.
        """
        return self.ReadVersionDirect()[0]

    def ReadAPIVersion(self) -> str:
        """
        Reads API version from adapter drivers.

        All this function does is call ReadVersionDirect() and return its second element.
        """
        return self.ReadVersionDirect()[1]

    def ReadDetailedVersion(self, ClientID : int, APIVersionBuffer : bytes, 
                            DLLVersionBuffer : bytes, FWVersionBuffer : bytes):
        """
        RP1210_ReadDetailedVersion function in all its glory. Provide it with three buffers via
        create_string_buffer(17).

        Returns an error code if the function ran into an error. This will generally be:
        - ERR_DLL_NOT_INITIALIZED
        - ERR_HARDWARE_NOT_RESPONDING
        - ERR_INVALID_CLIENT_ID

        Usage of ReadDetailedVersionDirect() instead of this function is recommended.

        This is an RP1210C function. If your adapter drivers aren't following the RP1210C standard,
        this function will return 128 (ERR_DLL_NOT_INITIALIZED).
        """
        self.getDLL()   # set rp1210c flag
        if not self._conforms_to_rp1210c:
            return 128
        return self.getDLL().RP1210_ReadDetailedVersion(ClientID, APIVersionBuffer, 
                                                        DLLVersionBuffer, FWVersionBuffer)
        
    def ReadDetailedVersionDirect(self, ClientID : int) -> tuple:
        """
        Reads API, DLL, and adapter firmware version info. Returns a tuple containing (in order):
        - APIVersionInfo (str)
        - DLLVersionInfo (str)
        - FWVersionInfo (str) (this is from the adapter)

        This function communicates with your adapter to read firmware info.

        This is an RP1210C function. If your adapter drivers aren't following the RP1210C standard,
        this function will return empty strings.
        """
        self.getDLL()   # set rp1210c flag
        if not self._conforms_to_rp1210c:
            return ("", "", "")
        APIVersionInfo = create_string_buffer(17)
        DLLVersionInfo = create_string_buffer(17)
        FWVersionInfo = create_string_buffer(17)
        self.getDLL().RP1210_ReadDetailedVersion(ClientID, APIVersionInfo, DLLVersionInfo, FWVersionInfo)
        return (str(APIVersionInfo.value, "utf-8"), str(DLLVersionInfo.value, "utf-8"), 
                str(FWVersionInfo.value, "utf-8"))

    def GetErrorMsg(self, ErrorCode : int) -> str:
        """
        Returns 'a textual representation of the last error code that occurred by that client in an
        application.'
        - ErrorCode = 'Numerical value for the last error which occurred.'

        If GetErrorMsg fails, this function will return the GetErrorMsg code (generally ERR_CODE_NOT_FOUND).
        """
        ErrorMsg = create_string_buffer(80)
        ret_code = self.getDLL().RP1210_GetErrorMsg(ErrorCode, ErrorMsg)
        if ret_code == 0:
            return str(ErrorMsg.value, "utf-8")
        else:
            return translateErrorCode(ErrorCode)

    def GetHardwareStatus(self, ClientID : int, ClientInfoBuffer : bytes, BufferSize : int = 0) -> int:
        """
        Calls GetHardwareStatus and places the result in ClientInfoBuffer. Returns an error code.

        Use create_str_buffer() to create the buffer.

        ClientInfoBuffer size must range between 16 and 64, and must be a multiple of 2.

        You can also just use GetHardwareStatusDirect() and not worry about buffers.
        """
        if not BufferSize:
            BufferSize = len(ClientInfoBuffer)
        return self.getDLL().RP1210_GetHardwareStatus(ClientID, ClientInfoBuffer, BufferSize, 0) & 0xFFFF

    def GetHardwareStatusDirect(self, ClientID : int, BufferSize = 16) -> bytes:
        """
        Calls GetHardwareStatus and returns the result directly.

        BufferSize must range between 16 and 64, and must be a multiple of 2 (defaults to 64).
        """
        ClientInfo = create_string_buffer(BufferSize)
        self.getDLL().RP1210_GetHardwareStatus(ClientID, ClientInfo, BufferSize, 0)
        return ClientInfo.raw

    def SendCommand(self, CommandNumber : int, ClientID : int, ClientCommand = b"", MessageSize = 0) -> int:
        """
        Calls RP1210_SendCommand.

        MessageSize will automatically be set to len(ClientCommand) if it is left 0.
        
        You really want to read the RP1210C documentation for this one.
        """
        if MessageSize == 0 and ClientCommand != b"":
            MessageSize = len(ClientCommand)
        return self.getDLL().RP1210_SendCommand(CommandNumber, ClientID, ClientCommand, MessageSize) & 0xFFFF

    def _init_functions(self):
        """Give Python type hints for interfacing with the DLL."""
        self.dll.RP1210_ClientConnect.argtypes = [c_long, c_short, c_char_p, c_long, c_long, c_short]
        self.dll.RP1210_ClientDisconnect.argtypes = [c_short]
        self.dll.RP1210_SendMessage.argtypes = [c_short, c_char_p, c_short, c_short, c_short]
        self.dll.RP1210_ReadMessage.argtypes = [c_short, c_char_p, c_short, c_short]
        self.dll.RP1210_ReadVersion.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        self.dll.RP1210_GetErrorMsg.argtypes = [c_short, c_char_p]
        self.dll.RP1210_GetHardwareStatus.argtypes = [c_short, c_char_p, c_short, c_short]
        self.dll.RP1210_SendCommand.argtypes = [c_short, c_short, c_char_p, c_short]
        # RP1210C functions
        try:
            self.dll.RP1210_ReadDetailedVersion.argtypes = [c_short, c_char_p, c_char_p, c_char_p]
            self.dll.RP1210_GetLastErrorMsg.argtypes = [c_short, POINTER(c_int32), c_char_p, c_short]
            self.dll.RP1210_Ioctl.argtypes = [c_short, c_long, c_void_p, c_void_p]
        except Exception: # RP1210C functions not supported
            self._conforms_to_rp1210c = False

    def _get_alternate_dll_path(self) -> str:
        """
        Some adapter vendors (looking at you, Actia) install their drivers in the wrong directory.
        This function returns the dll path in that directory.
        """
        return os.path.join(os.environ["WINDIR"], self._api_name + ".dll")

    def _validate_and_fix_clientid(self, clientID) -> int:
        """
        Noregon DLA2 adapters have an issue where they return a bunch of garbage along with the
        ClientID when calling ClientConnect. This is the fix for that.

        PCAN adapters also have an issue when trying to connect to adapters that aren't plugged in,
        so they get to join the hall of shame.
        """
        if clientID < 0: # some functions return negative value for error code
            clientID *= -1
        clientID &= 0xFFFF # Noregon can add garbage to leading bytes
        if clientID > 0x8000: # catches 2's complement unsigned ints
            clientID = 0xFFFF - clientID
        if self._api_name == "PEAKRP32" and clientID > 64:
            # PCAN drivers give invalid ClientID if it equals 114 (but cover wider range for safety) 
            clientID = 129  # ERR_INVALID_CLIENT_ID
        return clientID

class RP1210VendorList:
    """
    Loads and stores a list of all RP1210 adapter vendors specified in RP121032.ini (each vendor
    gets its own RP1210Config object).
    
    Also points to a specific RP1210Config object and a device within that RP1210Config. This feature is
    intended to be used with a couple of combo boxes that allow for the selection of RP1210 vendors
    and devices.

    - Access the RP1210Config object that is currently being pointed to with `getVendor()`.
    - Access the RP1210API object that is currently being pointed to with with `getAPI()`.
    - Set vendor index with `setVendorIndex()`.
    - Set device index with `setDeviceIndex()`. This is NOT deviceID!
    - If you have a vendor name but not index, use `getVendorIndex(api_name)` to find the index.
    """
    def __init__(self, rp121032_path : str = None, api_dir : str = None, config_dir : str = None):
        # super().__init__()
        self.vendors = [] #type: list[RP1210Config]
        self.vendorIndex = 0
        self.deviceIndex = 0
        self._rp121032_path = rp121032_path
        self._api_path = api_dir
        self._config_path = config_dir
        self.populate()

    def __getitem__(self, index : int) -> RP1210Config:
        return self.vendors[index]

    def __bool__(self) -> bool:
        return self.numVendors() != 0

    def __len__(self) -> int:
        return self.numVendors()

    def __str__(self) -> str:
        """
        Returns a list of api - vendor names
        """
        return ', '.join([str(i) for i in self.getVendorList()])

    def populate(self) -> None:
        """
        Populates vendors from RP121032.ini. Initializes an RP1210Config object for each vendor name
        that is found.
        """
        self.vendors.clear()
        api_list = getAPINames(self._rp121032_path)
        try:
            for api_name in api_list:
                try:
                    self.vendors.append(RP1210Config(api_name, self._api_path, self._config_path))
                except Exception:
                    # skip this API if its .ini file can't be parsed
                    pass
        except Exception:
            self.vendors = []

    def getList(self) -> list[RP1210Config]:
        """
        Returns list of stored RP1210Config objects (e.g. list of vendors).
        """
        return self.vendors

    def getVendorList(self) -> list[RP1210Config]:
        """Same as getList()."""
        return self.getList()

    def getAPI(self) -> RP1210API:
        """
        Returns RP1210API object pointed to by current vendor index and device index.
        
        Returns None on error.
        """
        try:
            return self.getCurrentVendor().getAPI()
        except Exception:
            return None

    def numVendors(self) -> int:
        """Returns number of vendors stored in vendor list."""
        try:
            return len(self.vendors)
        except Exception:
            return 0

    def numDevices(self) -> int:
        """Returns number of devices supported by current vendor."""
        try:
            return len(self.getCurrentVendor().getDevices())
        except Exception:
            return 0

    def setVendorIndex(self, index : int) -> None:
        """
        Set index of current vendor.
        """
        self.vendorIndex = index
        self.deviceIndex = 0

    def setVendor(self, api_name : str) -> None:
        """
        Sets current vendor by api_name (e.g. NULN2R32).

        Will set index to 0 if api_name is not found in RP121032.ini.
        """
        index = self.getVendorIndex(api_name)
        self.setVendorIndex(index)

    def setDeviceIndex(self, index : int) -> None:
        """
        Sets index of current device.
        """
        self.deviceIndex = index

    def setDevice(self, deviceID) -> None: 
        """
        Sets current device to device matching deviceID.
        """
        index = self.getDeviceIndex(deviceID)
        self.setDeviceIndex(index)

    def getDeviceIndex(self, deviceID = -1) -> int:
        """
        Returns index of device matching deviceID for current vendor. Returns 0 if no match is found.

        Returns current device index if no deviceID is provided.
        """
        if deviceID == -1:
            return self.deviceIndex
        index = 0
        try:
            for device in self.getCurrentVendor().getDevices():
                if device.getID() == deviceID:
                    return index
                index = index + 1
        except Exception:
            return 0
        return 0

    def getVendor(self, index : int = None) -> RP1210Config:
        """
        Returns RP1210Config object in vendor list at specified index.

        Will return current vendor if no index is provided.
        
        Will return None on error.
        """
        try:
            if index is None:
                return self.getCurrentVendor()
            if isinstance(index, str):
                return self.vendors[self.getVendorIndex(index)]
            return self.vendors[index]
        except Exception:
            return None

    def getVendorIndex(self, api_name = "") -> int:
        """
        Returns index of vendor in list that matches given vendor's api name.

        If API name is left blank, will return current vendor index instead.

        Returns 0 (start of list) if vendor is not found in list.
        """
        if api_name == "":
            return self.vendorIndex
        index = 0
        try:
            for vendor in self.vendors:
                if vendor.getAPIName() == api_name:
                    return index
                index += 1
        except Exception:
            return 0
        # if no matching vendor found in list:
        return 0

    def getCurrentVendor(self) -> RP1210Config:
        """
        Returns RP1210Config object pointed to by vendor_index.

        Will return None on error.
        """
        try:
            return self.vendors[self.vendorIndex]
        except Exception:
            return None

    def getVendorName(self) -> str:
        """
        Returns 'Name' field from currently selected vendor's VendorInformation.
        """
        try:
            return self.getCurrentVendor().getName()
        except Exception:
            return ""

    def getCurrentDevice(self) -> RP1210Device:
        """
        Returns RP1210Device object pointed to by device_index.

        Will return None on error.
        """
        try:
            return self.getCurrentVendor().getDevices()[self.deviceIndex]
        except IndexError: # check for index out of bounds
            # if DeviceList holds zero devices, there's a bigger issue
            if len(self.getCurrentVendor().getDevices()) == 0:
                return None
            # if index is out of bounds, reset it to position 0
            self.deviceIndex = 0
            return self.getCurrentDevice()
        except Exception:
            return None

    def getDeviceID(self) -> int:
        """
        Returns DeviceID of current device.

        Returns -1 if current device's DeviceID field is invalid.
        """
        try:
            return self.getCurrentDevice().getID()
        except Exception:
            return -1

    def getVendorNames(self) -> list[str]:
        """
        Generates a list of vendor names that are listed in RP1210.ini file
        """
        return [vendor.getName() for vendor in self.getVendorList()]

    def getAPINames(self) -> list[str]:
        """
        Generates a list of api names that are listed in RP1210.ini file
        """
        return [api.getAPIName() for api in self.getVendorList()]

    def getDeviceIDs(self) -> list[int]:
        """
        Generates a list of device IDs based on current vendor
        """
        deviceIDs = self.getCurrentVendor().getDeviceIDs()
        return deviceIDs

class RP1210Client(RP1210VendorList):
    """
    Stores a list of all adapter vendors and devices read from .ini files (child of VendorList), and
    handles connection with an adapter.
    """

    def __init__(self, rp121032_path : str = None, api_dir : str = None, config_dir : str = None) -> None:
        self.clientID = 128 # DLL_NOT_INITIALIZED
        super().__init__(rp121032_path, api_dir, config_dir)

    def __str__(self) -> str:
        try:
            return self.getCurrentVendor().getName()
        except Exception:
            return ""

    def __int__(self) -> int:
        return self.clientID
        
    ###################
    # CLASS FUNCTIONS #
    ###################

    def getClientID(self) -> int:
        """
        Returns clientID received from ClientConnect command (which you call via `connect()`).

        If `connect()` has not yet been called, will default to 128 (DLL_NOT_INITIALIZED).

        Will return -1 if there was an error calling ClientConnect.
        """
        return self.clientID

    ####################
    # RP1210 FUNCTIONS #
    ####################

    def connect(self, protocol = b"J1939:Baud=Auto") -> int:
        """
        Calls ClientConnect w/ specified protocol string, then stores resultant clientID.

        Returns clientID; will return 128 (ERR_DLL_NOT_INITIALIZED) if there's an error.
        """
        try:
            # if vendor .ini file is invalid, don't try to connect
            if not self.getCurrentVendor().isValid():
                return 128 # DLL_NOT_INITIALIZED
            deviceID = self.getDeviceID()
            self.clientID = self.getAPI().ClientConnect(deviceID, protocol) & 0xFFFF
            return self.clientID
        except Exception:
            return 128 # DLL_NOT_INITIALIZED

    def disconnect(self) -> int:
        """
        Disconnects from adapter.
        
        Returns 0 if successful, or >127 if it failed.
            You can use translateClientID() to translate the failure code.
        """
        try:
            return self.getAPI().ClientDisconnect(self.clientID) & 0xFFFF
        except Exception:
            return 128 # DLL_NOT_INITIALIZED

    def command(self, CommandNumber, ClientCommand = b"", MessageSize = 0) -> int:
        """
        Calls RP1210_SendCommand with current clientID.

        MessageSize will default to len(ClientCommand) if it is left 0.
        """
        try:
            return self.getAPI().SendCommand(CommandNumber, self.clientID, ClientCommand, MessageSize)  & 0xFFFF
        except Exception:
            return -1

    def rx(self, buffer_size = 256, blocking = 0) -> bytes:
        """
        Calls ReadMessage, but generates and returns its own RxBuffer value.
        - buffer_size = the size of the buffer in bytes. Defaults to 256.
        - blocking = sets NON_BLOCKING_IO or BLOCKING_IO. Defaults to NON_BLOCKING_IO.

        Output still includes leading 4 timestamp bytes, if applicable.

        Unlike most of the other functions in this module, this function WILL throw an exception
        if the relevant RP1210API isn't able to be initialized!
        """
        return self.getAPI().ReadDirect(self.getClientID(), buffer_size, blocking)

    def tx(self, message, msg_size = 0) -> int:
        """
        Send a message to the databus your adapter is connected to.
        - message = message you want to send
        - msg_size = message size in bytes (including qualifier bytes like timestamp, if applicable)
            - Will default to len(message) if msg_size = 0
        
        Use a message function provided with this package (e.g. toJ1939Message()) to generate the
        message. Or just do it yourself, I'm not the boss of you.

        Returns 0 if successful, or >127 if it failed.
            You can use translateClientID() to translate the failure code.
        """
        try:
            if msg_size == 0:
                msg_size = len(message)
            return self.getAPI().SendMessage(self.clientID, sanitize_msg_param(message, msg_size), msg_size)
        except Exception:
            return 128 # DLL_NOT_INITIALIZED

    #####################
    # COMMAND FUNCTIONS #
    #####################

    def resetDevice(self) -> int:
        """
        Reset Device (0) (0 bytes)

        RP1210_RESET_DEVICE only works if only one client is connected to the adapter, and does
        the exact same thing as if you called the function ClientDisconnect.
        """
        return self.command(0)
    
    def setAllFiltersToPass(self) -> int:
        """
        Set All Filter States to Pass (3) (0 bytes)
        """
        return self.command(3)

    def setJ1939Filters(self, filter_flag : int, pgn = 0, source = 0, dest = 0) -> int:
        """
        Set Message Filtering for J1939 (4) (7 bytes)

        Args:
        - Filter flag (1 byte) - filter flag integer/bytecode.
            - FILTER_PGN (1), FILTER_SOURCE (2), FILTER_DESTINATION (4)
            - J1939_FILTERS dict is available for convenience.
        - PGN (3 bytes) - the PGN that needs to be filtered.
        - Source Address (1 byte) - the source address that needs to be filtered.
        - Destination Address (1 byte) - the destination address that needs to be filtered.

        Args pgn, source, and dest only do anything if they are set with filter_flag. If they aren't,
        they will be ignored.

        You can specifiy filter_flag and keyword arguments instead of entering useless values for
        pgn, source, or dest.
        """
        cmd_num = 4
        cmd_data = Commands.setJ1939Filters(filter_flag, pgn, source, dest)
        cmd_size = 7
        return self.command(cmd_num, cmd_data, cmd_size)

    def setCANFilters(self, can_type, mask, header) -> int:
        """
        Set Message Filtering for CAN (5) (9 bytes)

        Args:
        - CAN Type (1 byte) - 0x00 for STANDARD_CAN, 0x01 for EXTENDED_CAN.
            - See dict CAN_TYPES for other types.
        - Mask (4 bytes) - a bitwise mask that indicates which bits in the header need to be matched.
            - Big endian; "1" means a value is important; "0" means a value is unimportant.
        - Header (4 bytes) - "Indicates what value is required for each bit of interest".

        This is one of those functions that you're going to want the RP1210C documentation for.
        """
        cmd_num = 5
        cmd_data = Commands.setCANFilters(can_type, mask, header)
        cmd_size = 9
        return self.command(cmd_num, cmd_data, cmd_size)
        
    def setEcho(self, echo_on = True) -> int:
        """
        Set Echo Transmitted Messages (16) (1 byte)

        Args:
        - Echo on/off (bool) - False for no echo, True for echo.
        """
        cmd_num = 16
        cmd_data = Commands.setEcho(echo_on)
        cmd_size = 1
        return self.command(cmd_num, cmd_data, cmd_size)

    def setAllFiltersToDiscard(self) -> int:
        """
        Set All Filter States to Discard (17) (0 bytes)
        """
        return self.command(17)

    def setMessageReceive(self, receive_messages = True) -> int:
        """
        Set Message Receive (18)

        Args:
        - Receive on/off : True = RECEIVE_ON, False = RECEIVE_OFF.
        """
        cmd_num = 18
        cmd_data = Commands.setMessageReceive(receive_messages)
        cmd_size = 1
        return self.command(cmd_num, cmd_data, cmd_size)

    def protectJ1939Address(self, address_to_claim, network_mgt_name, blocking = True) -> int:
        """
        Protect J1939 Address (19) (10 bytes)

        This command claims an address on the J1939 bus.
        - address_to_claim (1 byte) - 8-bit address to claim on the J1939 bus.
        - network_mgt_name (8 bytes) - 8-byte name of client on network (this is you!)
            - See J1939 network management standard!
            - Lowest name takes priority if two devices try to claim the same address
        - blocking (bool) - True will block until done, False will return before completion
        """
        cmd_num = 19
        cmd_data = Commands.protectJ1939Address(address_to_claim, network_mgt_name, blocking)
        cmd_size = 10
        return self.command(cmd_num, cmd_data, cmd_size)

    def releaseJ1939Address(self, address) -> int:
        """
        Release a J1939 Address (31)

        Args:
        - Address (1 byte) - the address to release.

        This doesn't do anything special with the J1939 bus. All it does is tell your adapter not to
        use this address anymore.
        """
        cmd_num = 31
        cmd_data = Commands.releaseJ1939Address(address)
        cmd_size = 1
        return self.command(cmd_num, cmd_data, cmd_size)

    def setJ1939FilterType(self, filter_type : Literal[0, 1]) -> int:
        """
        RP1210_Set_J1939_Filter_Type (25) (1 byte)

        filter_type:
        - 0 = FILTER_INCLUSIVE
        - 1 = FILTER_EXCLUSIVE
        """
        cmd_num = 25
        cmd_data = Commands.setFilterType(filter_type)
        cmd_size = 1
        return self.command(cmd_num, cmd_data, cmd_size)

    def setCANFilterType(self, filter_type : Literal[0, 1]) -> int:
        """
        RP1210_Set_CAN_Filter_Type (26) (1 byte)

        filter_type:
        - 0 = FILTER_INCLUSIVE
        - 1 = FILTER_EXCLUSIVE
        """
        cmd_num = 26
        cmd_data = Commands.setFilterType(filter_type)
        cmd_size = 1
        return self.command(cmd_num, cmd_data, cmd_size)

    def setJ1939InterpacketTime(self, time_in_ms : int) -> int:
        """
        Set J1939 Broadcast Interpacket Timing (27) (4 bytes)

        Args:
        - time_in_ms - interpacket time in milliseconds (unsigned 32-bit int)
        """
        cmd_num = 27
        cmd_data = Commands.setJ1939InterpacketTime(time_in_ms)
        cmd_size = 1
        return self.command(cmd_num, cmd_data, cmd_size)

    def setMaxErrorMsgSize(self, msg_size : int) -> int:
        """
        Set Max Error Message Return Size (28) (2 bytes)

        Args:
        - msg_size - value in bytes for how large error messages are allowed to be.
            - Should be between 81 and 65535
        """
        cmd_num = 28
        cmd_data = Commands.setMaxErrorMsgSize(msg_size)
        cmd_size = 1
        return self.command(cmd_num, cmd_data, cmd_size)

    def disallowConnections(self) -> int:
        """
        Disallow Further Client Connections (29) (0 bytes)
        """
        return self.command(29)

    def setJ1939Baud(self, baud_code : int, wait_for_msg = True) -> int:
        """
        Set J1939 Baud Rate (37)

        Args:
        - baud_code - code that corresponds w/ desired baud rate
            - 125k = 4
            - 250k = 5
            - 500k = 6
            - 1000k = 7
        - wait_for_msg - should we apply the baud change after the current message is finished, or
                        apply the change right away?
        """
        cmd_num = 37
        cmd_data = Commands.setJ1939Baud(baud_code, wait_for_msg)
        cmd_size = 2
        return self.command(cmd_num, cmd_data, cmd_size)

    def setBlockingTimeout(self, block1 : int, block2 : int) -> int:
        """
        Set Blocking Timeout (215) (2 bytes)

        Block 1 and block 2 are multiplied together to determine the final blocking time in
        milliseconds. Set either block to 0 for infinite time.
        """
        cmd_num = 215
        cmd_data = Commands.setJ1939Baud(block1, block2)
        cmd_size = 2
        return self.command(cmd_num, cmd_data, cmd_size)

    def flushBuffers(self) -> int:
        """
        Flush the Send/Receive Buffers (39) (0 bytes)
        """
        return self.command(39)

    def getBaud(self) -> str:
        """
        Calls the RP1210_Get_Protocol_Connection_Speed (45) command and returns the value that is
        received as a string of up to 16 characters.
        """
        cmd_num = 45
        cmd_buffer = create_string_buffer(17)
        cmd_size = 17
        self.command(cmd_num, cmd_buffer, cmd_size)
        return str(cmd_buffer[:cmd_size]) # return first 16 bytes

    def setCANBaud(self, baud_code : int, wait_for_msg = True):
        """
        Set CAN Baud Rate (47) (2 bytes)

        Args:
        - baud_code - code that corresponds w/ desired baud rate
            - 9600 = 0
            - 19200 = 1
            - 38400 = 2
            - 57600 = 3
            - 125k = 4
            - 250k = 5
            - 500k = 6
            - 1000k = 7
        - wait_for_msg - should we apply the baud change after the current message is finished, or
                        apply the change right away?
        """
        cmd_num = 47
        cmd_data = Commands.setCANBaud(baud_code, wait_for_msg)
        cmd_size = 2
        return self.command(cmd_num, cmd_data, cmd_size) & 0xFFFF
