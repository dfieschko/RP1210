import os
import configparser
from configparser import ConfigParser
from ctypes import c_char_p, c_long, c_short, cdll, CDLL

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
    151: "ERR BUS OFF",
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
    220: "ERR OS NOT SUPPORTED",
    222: "ERR_COMMAND_QUEUE_IS_FULL",
    224: "ERR_CANNOT_SET_CAN_BAUDRATE",
    225: "ERR_CANNOT_CLAIM_BROADCAST_ADDRESS",
    226: "ERR_OUT_OF_ADDRESS_RESOURCES",
    227: "ERR_ADDRESS_RELEASE_FAILED",
    230: "ERR_COMM_DEVICE_IN_USE",
    441: "ERR_DATA_LINK_CONFLICT",
    453: "ERR_ADAPTER_NOT_RESPONDING",
    454: "ERR_CAN_BAUD_SET_NONSTANDARD",
    455: "ERR_MULTIPLE_CONNECTIONS_NOT_ALLOWED_NOW",
    456: "ERR_J1708_BAUD_SET_NONSTANDARD",
    457: "ERR_J1939_BAUD_SET_NONSTANDARD",
    458: "ERR_IS015765_BAUD_SET_NONSTANDARD",
    600: "ERR_INVALID_IOCTL_ID",
    601: "ERR_NULL_PARAMETER",
    602: "ERR_HARDWARE_NOT_SUPPORTED"}

def translateClientID(nClientID :int) -> str:
    """
    Matches clientID with error string in RP1210_ERRORS.

    NO_ERRORS has been expanded to cover clientID = 0 to 127.
    
    If there is no match, returns the clientID as str.
    """
    if 0 <= nClientID < 128:
        return "NO_ERRORS"
    return RP1210_ERRORS.get(nClientID, str(nClientID))

class RP121032Parser(ConfigParser):
    """
    A simple little class for reading API names from RP121032.ini.

    Just initialize the class and call getAPINames() to get the API names. Then, you can initialize
    an RP1210Interface object using one of the API names.

    Doesn't handle any exceptions on its own, since if this fails none of your RP1210 functions
    will work.
    - Will throw FileNotFoundError if RP121032.ini isn't found.
    - Will throw ConfigParser exceptions if something goes wrong on the ConfigParser end.
    """

    def __init__(self) -> None:
        super().__init__()

    def getAPINames(self) -> list[str]:
        """
        Returns list of API names from RP121032.ini.

        If file hasn't already been read, will try to read the file first via populate().
        """
        if not self or not self.has_section("RP1210Support"):
            self.populate()
        return self["RP1210Support"]["APIImplementations"].split(",")

    def populate(self) -> list[str]:
        """
        Reads RP121032.ini in Windows directory.
        These API name strings correspond with .ini filenames.

        Raises FileNotFoundError if RP121032.ini isn't found in WINDOWS directory.

        Raises your standard ConfigParser exceptions if something goes wrong w/ reading the file.
        """
        rp121032_path = os.path.join(os.environ["WINDIR"], "RP121032.ini")
        if not os.path.isfile(rp121032_path):
            raise FileNotFoundError
        self.read(rp121032_path)
    
class RP1210Interface(ConfigParser):
    """
    Reads & stores API information. It's a child of ConfigParser. Use RP121032Parser to get an
    RP1210 API name to feed to this class.

    This class has functions for reading EVERY SINGLE data field defined in the RP1210C standard.
    As such, it is embarrassingly long. Most of it is just docstrings, though.

    This class holds an instance of RP1210API, which you can use to call RP1210 functions.
    The interface is accessed via the function api(), e.g.:
        nexiq = RP1210Interface("NULN2R32")
         clientID = nexiq.api().ClientConnect(args)

    You can use str() to generate a string to display in your Vendors dropdown.
    """
    def __init__(self, api_name : str) -> None:
        super().__init__()
        self.api_name = api_name
        self.api_valid = True
        self.devices = []   # type: list[RP1210Device]
        self.dll = None
        self.API = RP1210API()

        self.populate()

    def __str__(self) -> str:
        """
        Returns a string that you'd typically put in a vendor selection box.
        
        Format: "api_name - adapter_description"

        Appends " - (drivers invalid)" if drivers failed to load.
        """
        if self.api_valid:
            err_str = ""
        else:
            err_str = " - (drivers invalid)"
        return self.getAPIName() + " - " + self.getName() + err_str

    def api(self):
        """
        Returns RP1210API object that can be used to call RP1210 functions.
        
        If DLL has not yet been loaded, will load DLL before returning API.
        """
        if not self.dll:
            self.loadDLL()
        return self.API

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
        
        If you already called loadDLL(), you can call getDLL() to get the DLL you loaded previously.
        """
        try:
            try:
                path = self.api_name + ".dll"
                dll = cdll.LoadLibrary(path)
            except WindowsError:
                # Try "DLL installed in wrong directory" band-aid
                path = self.__get_dll_path_aux()
                dll = cdll.LoadLibrary(path)
            self.API.setDLL(dll)
            self.dll = dll
            return dll
        except Exception: # RIP
            self.api_valid = False
            return None

    def isValid(self) -> bool:
        """
        Returns self.api_valid, which is set to False if drivers fail to load,
        devices can't be read, etc.

        This function DOES NOT run through any checks before returning api_valid - so don't
        call it right away!
            e.g. you can't call isValid() to see if you can call getDLL() - call getDLL() first.
        """
        return self.api_valid

    def getAPIName(self) -> str:
        """Returns API name (i.e. the name of the .ini and .dll files)"""
        return self.api_name

    def getName(self) -> str:
        """
        Returns 'Name' field from VendorInformation section.

        Will return "(Vendor Name Missing)" if the 'Name' field isn't found.
        
        'Description' would be a better name for this field, but I'm not the one who came up
        with the RP1210 standard ¯\\\_(ツ)_/¯.
        """
        if not self.has_option("VendorInformation", "Name"):
            return "(Vendor Name Missing)"
        return self.get("VendorInformation", "Name")

    def getAddress1(self) -> str:
        """
        Returns 'Address1' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Address1"):
            return ""
        return self.get("VendorInformation", "Address1")

    def getAddress2(self) -> str:
        """
        Returns 'Address2' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Address2"):
            return ""
        return self.get("VendorInformation", "Address2")

    def getCity(self) -> str:
        """
        Returns 'Address2' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "City"):
            return ""
        return self.get("VendorInformation", "City")

    def getState(self) -> str:
        """
        Returns 'State' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "State"):
            return ""
        return self.get("VendorInformation", "State")

    def getCountry(self) -> str:
        """
        Returns 'Country' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Country"):
            return ""
        return self.get("VendorInformation", "Country")

    def getPostal(self) -> str:
        """
        Returns 'Postal' field (zipcode) from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Postal"):
            return ""
        return self.get("VendorInformation", "Postal")

    def getTelephone(self) -> str:
        """
        Returns 'Telephone' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Telephone"):
            return ""
        return self.get("VendorInformation", "Telephone")

    def getFax(self) -> str:
        """
        Returns 'Fax' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Fax"):
            return ""
        return self.get("VendorInformation", "Fax")

    def getVendorURL(self) -> str:
        """
        Returns the VendorURL field in VendorInformation section.
        
        Returns empty string if VendorURL field isn't found.
        """
        if not self.has_option("VendorInformation", "VendorURL"):
            return ""
        return self.get("VendorInformation", "VendorURL")

    def getVersion(self) -> int:
        """
        Returns the 'Version' field in VendorInformation section.
        
        Returns None if Version field isn't found.
        """
        if not self.has_option("VendorInformation", "Version"):
            return None
        try:
            return self.getint("VendorInformation", "Version")
        except ValueError:
            return None

    def autoDetectCapable(self) -> bool:
        """
        Returns the 'AutoDetectCapable' field in VendorInformation section.

        Returns False if the field isn't found.
        """
        if not self.has_option("VendorInformation", "AutoDetectCapable"):
            return False
        try:
            return self.getboolean("VendorInformation", "AutoDetectCapable")
        except ValueError:
            return False

    def getTimeStampWeight(self) -> float:
        """
        Returns the 'TimeStampWeight' field in VendorInformation section.

        Returns None if the field isn't found.
        """
        if not self.has_option("VendorInformation", "TimeStampWeight"):
            return None
        try:
            return self.getfloat("VendorInformation", "TimeStampWeight")
        except ValueError:
            return None

    def getMessageString(self) -> str:
        """
        Returns the 'MessageString' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "MessageString"):
            return ""
        return self.get("VendorInformation", "MessageString")

    def getErrorString(self) -> str:
        """
        Returns the 'ErrorString' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "ErrorString"):
            return ""
        return self.get("VendorInformation", "ErrorString")

    def getRP1210Version(self) -> str:
        """
        Returns the 'RP1210' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "RP1210Version"):
            return ""
        return self.get("VendorInformation", "RP1210Version")

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
        if not self.has_option("VendorInformation", "DebugLevel"):
            return -1
        try:
            return self.getint("VendorInformation", "DebugLevel")
        except ValueError:
            return -1

    def getDebugFile(self) -> str:
        """
        Returns the 'DebugFile' field in VendorInformation section.

        This represents the absolute path to the debug/log file.

        Returns a blank string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "DebugFile"):
            return ""
        return self.get("VendorInformation", "DebugFile")

    def getDebugMode(self) -> int:
        """
        Returns the 'DebugMode' field in VendorInformation section.
        - 0 = Overwrite (completely destroying previous contents) 
        - 1 = Append (write to the end of the file, keeping any previous contents) 

        Returns None if the field isn't found.
        """
        if not self.has_option("VendorInformation", "DebugMode"):
            return None
        try:
            return self.getint("VendorInformation", "DebugMode")
        except ValueError:
            return None

    def getDebugFileSize(self) -> int:
        """
        Returns the 'DebugFileSize' field in VendorInformation section.
        
        This represents the maximum size in kilobytes that the debug file should be.
        If this field is missing (and debug logging is enabled), it defaults to 1024 KB (1MB).

        Returns 1024 (default size) if the field isn't found. Please note that if DebugLevel = -1,
        there will be no logging even if you receive a value of 1024 from this function.
        """
        if not self.has_option("VendorInformation", "DebugFileSize"):
            return 1024
        try:
            return self.getint("VendorInformation", "DebugFileSize")
        except ValueError:
            return 1024

    def getNumberOfSessions(self) -> int:
        """
        Returns the 'NumberOfRTSCTSSessions' field in VendorInformation section.

        'NumberOfRTSCTSSessions' is an integer representing the number of concurrent RTS/CTS
        transport sessions that the API supports per client.

        Returns 1 (default value) if the field isn't found.
        """
        if not self.has_option("VendorInformation", "NumberOfSessions"):
            return 1
        try:
            return self.getint("VendorInformation", "NumberOfSessions")
        except ValueError:
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
            return self["VendorInformation"]["CANFormatsSupported"].split(",")
        except Exception:
            return []

    def getJ1939FormatsSupported(self) -> list[int]:
        """
        Returns the 'J1939FormatsSupported' list in VendorInformation section.

        These numbers correspond with the CAN Formats described in section 12.8 of the RP1210C 
        documentation.

        Returns an empty list if the field isn't found.
        """
        if not self.has_option("VendorInformation", "J1939FormatsSupported"):
            return []
        try:
            return self["VendorInformation"]["J1939FormatsSupported"].split(",")
        except Exception:
            return []

    def populate(self):
        """Reads .ini file for the specified RP1210 API."""
        try:
            self.read(self.getPath())
        except configparser.Error:
            self.api_valid = False

    def getPath(self):
        """Returns absolute path to API config file."""
        return os.path.join(os.environ["WINDIR"], self.api_name + ".ini")

    def __get_dll_path_aux(self) -> str:
        """
        Some adapter vendors (looking at you, Actia) install their drivers in the wrong directory.
        This function returns the dll path in that directory.
        """
        return os.path.join(os.environ["WINDIR"], self.api_name + ".dll")

class RP1210API:
    """
    Interface with RP1210 API to call functions from your adapter's drivers.
    """
    def __init__(self) -> None:
        self.api_valid = False
        self.DLL = None

    def isValid(self) -> bool:
        """Returns api_valid boolean, which is set when the DLL is loaded."""
        return self.api_valid

    def setDLL(self, dll : CDLL):
        try:
            self.dll = dll
            if self.dll: # check it's not None
                self.__init_functions()
                self.api_valid = True
            else:
                self.api_valid = False
        except OSError:
            self.api_valid = False

    def __init_functions(self):
        self.dll.RP1210_ClientConnect.argtypes = [c_long, c_short, c_char_p, c_long, c_long, c_short]
        self.dll.RP1210_ClientDisconnect.argtypes = [c_short]
        self.dll.RP1210_SendMessage.argtypes = [c_short, c_char_p, c_short, c_short, c_short]
        self.dll.RP1210_ReadMessage.argtypes = [c_short, c_char_p, c_short, c_short]
        self.dll.RP1210_ReadVersion.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        self.dll.RP1210_GetErrorMsg.argtypes = [c_short, c_char_p]
        self.dll.RP1210_GetHardwareStatus.argtypes = [c_short, c_char_p, c_short, c_short]
        self.dll.RP1210_SendCommand.argtypes = [c_short, c_short, c_char_p, c_short]

class RP1210Device:
    """
    """
    def __init__(self) -> None:
        self.DeviceID = -1
        self.DeviceDescription = ""
        self.DeviceName = ""
        self.DeviceParams = ""
