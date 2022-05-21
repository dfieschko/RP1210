from configparser import ConfigParser
import os
from RP1210 import sanitize_msg_param
import RP1210
import pytest

from Test.test_0_vendorlist import RP121032_PATH

def delete_file(path : str):
    if os.path.exists(path):
        os.remove(path)

def create_file(path : str) -> ConfigParser:
    """creates an empty file."""
    parser = ConfigParser()
    with open(path, 'w') as file:
        parser.clear()
        parser.write(file)
    return parser
    
def test_getAPINames_notfound():
    """test getAPINames when file doesn't exist at path"""
    with pytest.raises(FileNotFoundError):
        path = "doesnt_exist.ini"
        result = RP1210.getAPINames(path)

def test_getAPINames_empty():
    """generate empty file and provide its path to getAPINames"""
    # generate file
    path = "getAPINames_empty.ini"
    create_file(path)
    # test output
    result = RP1210.getAPINames(path)
    assert result == []

def test_getAPINames_invalid():
    """generate an invalid file and provide its path to getAPINames"""
    # generate file
    path = "getAPINames_invalid.ini"
    parser = create_file(path)
    parser.add_section("[")
    with open(path, 'w') as file:
        parser.write(file)
    # test output
    assert RP1210.getAPINames(path) == []

def test_delete_files():
    """Deletes the files created by other tests."""
    delete_file("getAPINames_empty.ini")
    delete_file("getAPINames_invalid.ini")

def test_clientid_translation():
    assert RP1210.translateErrorCode(0) == "NO_ERRORS"
    assert RP1210.translateErrorCode(1) == "NO_ERRORS"
    assert RP1210.translateErrorCode(25) == "NO_ERRORS"
    assert RP1210.translateErrorCode(127) == "NO_ERRORS"
    assert RP1210.translateErrorCode(128) == "ERR_DLL_NOT_INITIALIZED"
    assert RP1210.translateErrorCode(151) == "ERR_BUS_OFF"
    assert RP1210.translateErrorCode(159) == "ERR_MESSAGE_NOT_SENT"
    assert RP1210.translateErrorCode(165) == "165"
    assert RP1210.translateErrorCode(207) == "ERR_DEVICE_NOT_SUPPORTED"
    assert RP1210.translateErrorCode(454) == "ERR_CAN_BAUD_SET_NONSTANDARD"
    assert RP1210.translateErrorCode(601) == "ERR_NULL_PARAMETER"
    assert RP1210.translateErrorCode(0xFFFF - 128) == "ERR_DLL_NOT_INITIALIZED"
    assert RP1210.translateErrorCode(-128) == "ERR_DLL_NOT_INITIALIZED"
    assert RP1210.translateErrorCode(0x48FFFFF) == "NO_ERRORS"
    assert RP1210.translateErrorCode(0x48FFF7F) == "ERR_DLL_NOT_INITIALIZED"
    assert RP1210.translateErrorCode("chungus") == "chungus"

def test_RP1210Interface_InvalidAPIName():
    """
    Tests the RP1210Interface class with an API name that doesn't exist.
    """
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.isValid() == False
    assert str(rp1210) == api_name + " - (Vendor Name Missing) - (drivers invalid)"
    assert rp1210.getAPIName() == api_name
    assert rp1210.getName() == "(Vendor Name Missing)"
    assert rp1210.getAddress1() == ""
    assert rp1210.getAddress2() == ""
    assert rp1210.getCity() == ""
    assert rp1210.getState() == ""
    assert rp1210.getCountry() == ""
    assert rp1210.getPostal() == ""
    assert rp1210.getTelephone() == ""
    assert rp1210.getFax() == ""
    assert rp1210.getVendorURL() == ""
    assert rp1210.getVersion() == ""
    assert rp1210.autoDetectCapable() == False
    assert rp1210.getCANAutoBaud() == False
    assert rp1210.getTimeStampWeight() == 1.0
    assert rp1210.getMessageString() == ""
    assert rp1210.getErrorString() == ""
    assert rp1210.getRP1210Version() == ""
    assert rp1210.getDebugLevel() == -1
    assert rp1210.getDebugFile() == ""
    assert rp1210.getDebugMode() == -1
    assert rp1210.getDebugFileSize() == 1024
    assert rp1210.getNumberOfSessions() == 1
    assert rp1210.getCANFormatsSupported() == []
    assert rp1210.getJ1939FormatsSupported() == []
    assert rp1210.getDeviceIDs() == []
    assert rp1210.getProtocolNames() == []
    assert rp1210.getProtocolIDs() == []
    assert rp1210.isValid() == False
    assert rp1210.getName() == rp1210.getDescription()

def test_InvalidAPIName_Devices_Protocols():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.getDeviceIDs() == []
    assert rp1210.getProtocolIDs() == []
    assert rp1210.getProtocol() == None
    assert rp1210.getProtocol(3) == None
    assert rp1210.getDevice(3) == None

def test_Invalid_Device():
    device = RP1210.RP1210Device(None)
    assert device.getID() == -1
    assert device.getDescription() == ""
    assert device.getName() == ""
    assert device.getParams() == ""
    assert device.getMultiCANChannels() == 0
    assert device.getMultiJ1939Channels() == 0
    assert str(device) == "(Invalid Device)"

def test_Invalid_Protocol():
    protocol = RP1210.RP1210Protocol(None)
    assert protocol.getDescription() == ""
    assert protocol.getSpeed() == []
    assert protocol.getString() == ""
    assert protocol.getParams() == ""
    assert protocol.getDevices() == []
    assert str(protocol) == " - "

def test_InvalidAPIName_load_dll():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.api.getDLL() == None
    assert rp1210.api.isValid() == False

def test_InvalidAPIName_conforms_to_rp1210C():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.api.conformsToRP1210C() == False

def test_sanitize_msg_param_bytes():
    assert sanitize_msg_param(b'0') == b'0'
    assert sanitize_msg_param(b'\x00') == b'\x00'
    assert sanitize_msg_param(b'16') == b'16'
    assert sanitize_msg_param(b'\x10') == b'\x10'
    assert sanitize_msg_param(b'0', 2) == b'\x000'
    assert sanitize_msg_param(b'\x00', 2) == b'\x00\x00'
    assert sanitize_msg_param(b'') == b''
    assert sanitize_msg_param(b'', 4) == b'\x00\x00\x00\x00'
    assert sanitize_msg_param(b'\x43\x64\xFE\x4A') == b'\x43\x64\xFE\x4A'
    assert sanitize_msg_param(b'\x43\x64\xFE\x4A', 3) == b'\x43\x64\xFE'
    assert sanitize_msg_param(b'\x43\x64\xFE\x4A', 3, 'little') == b'\x4A\xFE\x64'
    assert sanitize_msg_param(b'\x00\x00\x00') == b'\x00\x00\x00'
    assert sanitize_msg_param(b'\xFF\xFF\xFF') == b'\xFF\xFF\xFF'
    assert sanitize_msg_param(b'\xFF\xFF\xFF', 1) == b'\xFF'
    assert sanitize_msg_param(b'\x01\x02\x03', 1) == b'\x01'
    assert sanitize_msg_param(b'\x01\x02\x03', 1, 'little') == b'\x03'
    
def test_sanitize_msg_param_str():
     assert sanitize_msg_param("0") == b'0'
     assert sanitize_msg_param("16") == b'16'
     assert sanitize_msg_param("0", 2) == b'\x000'
     assert sanitize_msg_param("") == b''
     assert sanitize_msg_param("", 4) == b'\x00\x00\x00\x00'
     assert sanitize_msg_param("Boogity") == b"Boogity"
     assert sanitize_msg_param("Boogity", 4, 'little') == b'ytig'

def test_sanitize_msg_param_int():
    assert sanitize_msg_param(0) == b'\x00'
    assert sanitize_msg_param(16) == b'\x10'
    assert sanitize_msg_param(0x10) == b'\x10'
    assert sanitize_msg_param(0, 2) == b'\x00\x00'
    assert sanitize_msg_param(0xDEADBEEF, 4, 'little') == b'\xEF\xBE\xAD\xDE'
    assert sanitize_msg_param(0xDEADBEEF, 4, 'big') == b'\xDE\xAD\xBE\xEF'
    assert sanitize_msg_param(0xDEADBEEF, 4) == b'\xDE\xAD\xBE\xEF'
    assert sanitize_msg_param(0xDEADBEEFEE, 5) == b'\xDE\xAD\xBE\xEF\xEE'
    assert sanitize_msg_param(0xDEADBEEF, 6, 'little') == b'\xEF\xBE\xAD\xDE\x00\x00'
    assert sanitize_msg_param(0xDEADBEEF, 6, 'big') == b'\x00\x00\xDE\xAD\xBE\xEF'
    assert sanitize_msg_param(1234567) == b'\x12\xD6\x87'
    assert sanitize_msg_param(0x12345) == b'\x01\x23\x45'
    for x in range(0, 0xFFFF):
        assert x == int.from_bytes(sanitize_msg_param(x), 'big')
        assert x == int.from_bytes(sanitize_msg_param(x, 2, 'little'), 'little')

def test_sanitize_msg_param_bool():
    assert sanitize_msg_param(True, 1) == b'\x01'
    assert sanitize_msg_param(False, 1) == b'\x00'
    assert sanitize_msg_param(True, 2) == b'\x00\x01'
    assert sanitize_msg_param(False, 2) == b'\x00\x00'
    assert sanitize_msg_param(True, 2, 'little') == b'\x01\x00'
    assert sanitize_msg_param(True) == b'\x01'
    assert sanitize_msg_param(False) == b'\x00'

def test_sanitize_msg_param_typeerror():
    try:
        sanitize_msg_param(RP1210.RP1210VendorList())
    except TypeError:
        pass

def test_rp1210client_populate_logic():
    """Tests whether RP1210Client recognizes relevant drivers when adapter is disconnected."""
    vendors = []
    vendors.clear()
    api_list = RP1210.getAPINames(RP121032_PATH)
    if api_list == []:
        pytest.xfail("RP121032.ini not installed on system; calling XFAIL")
    try:
        for api_name in api_list:
            try:
                vendors.append(RP1210.RP1210Config(api_name))
            except Exception as err:
                # skip this API if its .ini file can't be parsed
                print(err)
                pass
    except Exception as err:
        print(err)
        vendors = []
    assert vendors != []

@pytest.mark.parametrize("input,expected",[
    (0, 0), (1, 1), (2, 2), (-1, 1), (-2, 2), (128, 128), (-128, 128), (0x10FA3, 0x0FA3),
    (-0x10FA3, 0x0FA3), (0xFFFF, 0), (0xFFFE, 1), (0xFFFD, 2), (-0xFFFD, 2), (-0xFFFFD, 2)
])
def test_driver_clientid_fix(input, expected):
    """Tests _driver_clientid_fix function in RP1210API."""
    class TestAPI(RP1210.RP1210API): # gotta make _driver_clientid_fix public
        def __init__(self, api_name: str, WorkingAPIDirectory: str = None) -> None:
            super().__init__(api_name, WorkingAPIDirectory)
    
        def fix(self, val : int):
            return self._validate_and_fix_clientid(val)

    api = TestAPI("test")
    assert api.fix(input) == expected

@pytest.mark.parametrize("input,expected",[
    (114, 129), (0,0), (-0xFFFF, 0), (-0xFFFE, 1)
])
def test_driver_clientid_fix_PEAKRP32(input, expected):
    """Tests _driver_clientid_fix function in RP1210API when using PEAKRP32 API."""
    class TestAPI(RP1210.RP1210API):
        def __init__(self, api_name: str, WorkingAPIDirectory: str = None) -> None:
            super().__init__(api_name, WorkingAPIDirectory)
    
        def fix(self, val : int):
            return self._validate_and_fix_clientid(val)

    api = TestAPI("PEAKRP32")
    assert api.fix(input) == expected
