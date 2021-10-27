from configparser import ConfigParser
import os
from RP1210C import RP1210
import RP1210C

def delete_file(path : str):
    if os.path.exists(path):
        os.remove(path)

def create_file(path : str) -> ConfigParser:
    """creates an empty file."""
    parser = ConfigParser()
    file = open(path, 'w')
    parser.clear()
    parser.write(file)
    return parser

def test_getAPINames():
    """
    The following drivers must be installed for this test:
    
    - Noregon DLA 2.0
    - Nexiq USB-Link 2
    """
    assert RP1210.getAPINames() != None
    api_names = RP1210.getAPINames()
    assert "DLAUSB32" in api_names
    assert "NULN2R32" in api_names
    

def test_getAPINames_notfound():
    """test getAPINames when file doesn't exist at path"""
    path = "doesnt_exist.ini"
    result = RP1210.getAPINames(path)
    assert result == []

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
    file = open(path, 'w')
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
    assert RP1210.translateErrorCode(623423401) == "623423401"
    assert RP1210.translateErrorCode(-128) == "ERR_DLL_NOT_INITIALIZED"

def test_RP1210Interface_InvalidAPIName():
    """
    Tests the RP1210Interface class with an API name that doesn't exist.
    """
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
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
    assert rp1210.CANAutoBaud() == False
    assert rp1210.getTimeStampWeight() == None
    assert rp1210.getMessageString() == ""
    assert rp1210.getErrorString() == ""
    assert rp1210.getRP1210Version() == ""
    assert rp1210.getDebugLevel() == -1
    assert rp1210.getDebugFile() == ""
    assert rp1210.getDebugMode() == None
    assert rp1210.getDebugFileSize() == 1024
    assert rp1210.getNumberOfSessions() == 1
    assert rp1210.getCANFormatsSupported() == []
    assert rp1210.getJ1939FormatsSupported() == []
    assert rp1210.getDevices() == []
    assert rp1210.getProtocols() == []

def test_InvalidAPIName_Devices_Protocols():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.getDevices() == []
    assert rp1210.getProtocols() == []
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
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.api.getDLL() == None

def test_RP1210Interface_NEMESIS():
    """
    Tests the RP1210Interface class with Cummins' NEMESIS dummy drivers, which are invalid.

    You must have these drivers installed to run this test.
    """
    api_name = "CMNSIM32"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.isValid() == False
    assert str(rp1210) == api_name + " - Cummins Inc. NEMESIS Mock RP1210 Driver - (drivers invalid)"
    devices = rp1210.getDevices()
    device = rp1210.getDevice(devices[0])
    assert str(device) == str(device.getID()) + " - " + device.getDescription()

def test_sanitize_msg_param():
    """Tests sanitize_msg_param()"""
    assert RP1210C.sanitize_msg_param(0) == b'\x00'
    assert RP1210C.sanitize_msg_param("0") == b'\x00'
    assert RP1210C.sanitize_msg_param(b'0') == b'\x00'
    assert RP1210C.sanitize_msg_param(b'\x00') == b'\x00'
    assert RP1210C.sanitize_msg_param(16) == b'\x10'
    assert RP1210C.sanitize_msg_param(0x10) == b'\x10'
    assert RP1210C.sanitize_msg_param("16") == b'\x10'
    assert RP1210C.sanitize_msg_param(b'16') == b'\x10'
    assert RP1210C.sanitize_msg_param(b'\x10') == b'\x10'
    assert RP1210C.sanitize_msg_param(0, 2) == b'\x00\x00'
    assert RP1210C.sanitize_msg_param("0", 2) == b'\x00\x00'
    assert RP1210C.sanitize_msg_param(b'0', 2) == b'\x00\x00'
    assert RP1210C.sanitize_msg_param(b'\x00', 2) == b'\x00\x00'
    assert RP1210C.sanitize_msg_param(0xDEADBEEF, 4, 'little') == b'\xEF\xBE\xAD\xDE'
    assert RP1210C.sanitize_msg_param(0xDEADBEEF, 4, 'big') == b'\xDE\xAD\xBE\xEF'
    assert RP1210C.sanitize_msg_param(0xDEADBEEF, 4) == b'\xDE\xAD\xBE\xEF'
    assert RP1210C.sanitize_msg_param(0xDEADBEEFEE, 5) == b'\xDE\xAD\xBE\xEF\xEE'
    assert RP1210C.sanitize_msg_param(0xDEADBEEF, 6, 'little') == b'\xEF\xBE\xAD\xDE\x00\x00'
    assert RP1210C.sanitize_msg_param(0xDEADBEEF, 6, 'big') == b'\x00\x00\xDE\xAD\xBE\xEF'
    for x in range(0, 0xFFFF):
        assert x == int.from_bytes(RP1210C.sanitize_msg_param(x), 'big')
        assert x == int.from_bytes(RP1210C.sanitize_msg_param(x, 2, 'little'), 'little')
        assert x == int.from_bytes(RP1210C.sanitize_msg_param(str(x)), 'big')
        assert x == int.from_bytes(RP1210C.sanitize_msg_param(str(x), 2, 'little'), 'little')
    assert RP1210C.sanitize_msg_param(1234567) == b'\x12\xD6\x87'
    assert RP1210C.sanitize_msg_param(0x12345) == b'\x01\x23\x45'
